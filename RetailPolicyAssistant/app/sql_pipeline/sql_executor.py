"""SQL Executor - Executes validated SQL queries."""

import asyncio
from typing import Optional
from sqlalchemy import text, event
from sqlalchemy.exc import SQLAlchemyError, OperationalError
from sqlalchemy.orm import Session
from app.database.session import SessionLocal
from app.guardrails.sql_safety_checker import SQLSafetyChecker


class SQLExecutor:
    """Executes SQL queries against the database with proper transaction handling."""

    def __init__(self, db_connection: Optional[Session] = None):
        self.db = db_connection
        self.safety_checker = SQLSafetyChecker()

    def execute(self, sql: str) -> dict:
        """Execute SQL query synchronously with transaction management."""
        try:
            # Validate and sanitize SQL
            safety_check = self.safety_checker.check(sql)
            if not safety_check.get("is_safe", False):
                return {
                    "success": False,
                    "error": f"Query blocked by security checks: unsafe keywords {safety_check.get('unsafe_keywords', [])}",
                    "row_count": 0,
                }

            # Create session if not provided
            session = self.db or SessionLocal()
            should_close = self.db is None

            try:
                # Execute query with transaction
                query = text(sql)
                result = session.execute(query)

                # Fetch results
                rows = result.fetchall()
                columns = result.keys() if result.keys() else []

                # Format results
                formatted_rows = [
                    {col: row[idx] for idx, col in enumerate(columns)}
                    for row in rows
                ]

                return {
                    "success": True,
                    "result": formatted_rows,
                    "row_count": len(formatted_rows),
                    "columns": list(columns),
                }
            finally:
                if should_close:
                    session.close()

        except OperationalError as e:
            return {
                "success": False,
                "error": f"Database connection error: {str(e)[:200]}",
                "row_count": 0,
            }
        except SQLAlchemyError as e:
            return {
                "success": False,
                "error": f"SQL execution error: {str(e)[:200]}",
                "row_count": 0,
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Unexpected error: {str(e)[:200]}",
                "row_count": 0,
            }

    async def execute_async(self, sql: str) -> dict:
        """Execute SQL query asynchronously."""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.execute, sql)

    async def execute_with_timeout(self, sql: str, timeout_seconds: int = 30) -> dict:
        """Execute SQL with timeout protection."""
        try:
            result = await asyncio.wait_for(
                self.execute_async(sql),
                timeout=timeout_seconds
            )
            return result
        except asyncio.TimeoutError:
            return {
                "success": False,
                "error": f"Query execution exceeded timeout of {timeout_seconds} seconds",
                "row_count": 0,
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Timeout handler error: {str(e)[:200]}",
                "row_count": 0,
            }

    def execute_with_transaction(self, sql: str, autocommit: bool = True) -> dict:
        """Execute SQL with explicit transaction management."""
        session = self.db or SessionLocal()
        should_close = self.db is None

        try:
            # Execute query
            query = text(sql)
            result = session.execute(query)

            # Fetch results before commit
            rows = result.fetchall()
            columns = result.keys() if result.keys() else []

            # Commit transaction
            if autocommit:
                session.commit()

            formatted_rows = [
                {col: row[idx] for idx, col in enumerate(columns)}
                for row in rows
            ]

            return {
                "success": True,
                "result": formatted_rows,
                "row_count": len(formatted_rows),
                "columns": list(columns),
                "transaction_committed": autocommit,
            }
        except Exception as e:
            # Rollback on error
            session.rollback()
            return {
                "success": False,
                "error": f"Transaction error: {str(e)[:200]}",
                "row_count": 0,
                "transaction_committed": False,
            }
        finally:
            if should_close:
                session.close()
