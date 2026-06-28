from app.sql import answer_sql


class SQLAgent:
    def run(self, query: str):
        return {
            "result": answer_sql(query)
        }
