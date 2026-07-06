#!/usr/bin/env python3
"""
Final Verification Test - Demonstrates the complete system working end-to-end
Tests:
1. Backend starts and health check passes
2. Documents are indexed in database
3. RAG retrieval finds relevant documents
4. API returns PDF-backed answers with sources
5. Confidence scores and risk assessment work
"""

import requests
import json
import time
import subprocess
import os
from pathlib import Path

class TestRunner:
    def __init__(self):
        self.api_url = "http://localhost:8000"
        self.passed = 0
        self.failed = 0
        self.token = None

    def print_section(self, title):
        print("\n" + "=" * 80)
        print(f"  {title}")
        print("=" * 80)

    def print_test(self, name, status, details=""):
        emoji = "PASS" if status else "FAIL"
        print(f"[{emoji}] {name}")
        if details:
            print(f"    {details}")
        if status:
            self.passed += 1
        else:
            self.failed += 1

    def wait_for_server(self, timeout=15):
        """Wait for backend server to start"""
        print("Waiting for backend server...", end=" ", flush=True)
        start = time.time()
        while time.time() - start < timeout:
            try:
                resp = requests.get(f"{self.api_url}/health", timeout=2)
                if resp.status_code == 200:
                    print("Ready!")
                    return True
            except:
                print(".", end="", flush=True)
                time.sleep(1)
        return False

    def test_health_check(self):
        """Test 1: Health Check"""
        try:
            resp = requests.get(f"{self.api_url}/health", timeout=5)
            self.print_test(
                "Health Check",
                resp.status_code == 200,
                f"Status: {resp.status_code}"
            )
            return resp.status_code == 200
        except Exception as e:
            self.print_test("Health Check", False, str(e)[:60])
            return False

    def test_get_token(self):
        """Test 2: Token Generation"""
        try:
            resp = requests.get(f"{self.api_url}/token", timeout=5)
            if resp.status_code == 200:
                data = resp.json()
                self.token = data.get("access_token")
                self.print_test(
                    "Token Generation",
                    bool(self.token),
                    f"Token: {self.token[:20]}..."
                )
                return bool(self.token)
            else:
                self.print_test("Token Generation", False, f"Status: {resp.status_code}")
                return False
        except Exception as e:
            self.print_test("Token Generation", False, str(e)[:60])
            return False

    def test_rag_query(self, query, expected_doc):
        """Test RAG query retrieval"""
        if not self.token:
            self.print_test(f"Query: {query[:50]}", False, "No token")
            return False

        try:
            headers = {"Authorization": f"Bearer {self.token}"}
            resp = requests.post(
                f"{self.api_url}/ask",
                json={"query": query},
                headers=headers,
                timeout=30
            )

            if resp.status_code != 200:
                self.print_test(f"Query: {query[:50]}", False, f"HTTP {resp.status_code}")
                return False

            data = resp.json()
            answer = data.get("result", {}).get("result", "")
            sources = data.get("sources", [])
            confidence = data.get("confidence_score", 0)

            # Check key criteria
            has_pdf_name = expected_doc in answer
            has_sources = len(sources) > 0
            high_confidence = confidence > 0.80
            has_answer_text = len(answer) > 100

            passed = has_pdf_name and has_sources and high_confidence and has_answer_text

            details = f"Conf: {confidence:.2f}, Sources: {len(sources)}, Has PDF: {has_pdf_name}"
            self.print_test(f"Query: {query[:45]}...", passed, details)

            return passed
        except Exception as e:
            self.print_test(f"Query: {query[:50]}", False, str(e)[:60])
            return False

    def test_source_citation(self):
        """Test 3: Source Citation"""
        if not self.token:
            self.print_test("Source Citation", False, "No token")
            return False

        try:
            headers = {"Authorization": f"Bearer {self.token}"}
            resp = requests.post(
                f"{self.api_url}/ask",
                json={"query": "What is our data retention policy?"},
                headers=headers,
                timeout=30
            )

            data = resp.json()
            sources = data.get("sources", [])

            # Verify source structure
            has_docs = any(isinstance(s, dict) and "document" in s for s in sources)
            has_pages = any(isinstance(s, dict) and "page" in s for s in sources)

            passed = has_docs and has_pages and len(sources) > 0
            self.print_test(
                "Source Citation",
                passed,
                f"Sources: {len(sources)}, Has docs: {has_docs}, Has pages: {has_pages}"
            )
            return passed
        except Exception as e:
            self.print_test("Source Citation", False, str(e)[:60])
            return False

    def test_confidence_and_risk(self):
        """Test 4: Confidence Scoring and Risk Assessment"""
        if not self.token:
            self.print_test("Confidence & Risk", False, "No token")
            return False

        try:
            headers = {"Authorization": f"Bearer {self.token}"}
            resp = requests.post(
                f"{self.api_url}/ask",
                json={"query": "What are the GDPR compliance requirements?"},
                headers=headers,
                timeout=30
            )

            data = resp.json()
            confidence = data.get("confidence_score", 0)
            risk_level = data.get("risk", {}).get("risk_level", "")

            # GDPR query should have high confidence and high risk
            passed = confidence > 0.75 and risk_level == "high"
            details = f"Confidence: {confidence}, Risk: {risk_level}"
            self.print_test("Confidence & Risk", passed, details)
            return passed
        except Exception as e:
            self.print_test("Confidence & Risk", False, str(e)[:60])
            return False

    def run_all_tests(self):
        """Run complete test suite"""
        self.print_section("FINAL VERIFICATION TEST")
        print(f"API URL: {self.api_url}\n")

        # Prerequisite: Check server
        print("Prerequisite: Checking server...")
        if not self.wait_for_server():
            print("ERROR: Backend server not running!")
            return False

        self.print_section("Test 1: Basic Connectivity")
        if not self.test_health_check():
            return False

        self.print_section("Test 2: Authentication")
        if not self.test_get_token():
            return False

        self.print_section("Test 3: RAG Query Retrieval from PDFs")
        test_queries = [
            ("What is our data retention policy for customer records?", "Data_Retention"),
            ("What are the GDPR compliance requirements?", "GDPR_Selected_Articles"),
            ("What is the information security access control policy?", "Information_Security"),
            ("What is our anti-bribery policy?", "Anti_Bribery"),
            ("What are the supplier vendor compliance requirements?", "Supplier_Vendor"),
        ]

        for query, expected_doc in test_queries:
            self.test_rag_query(query, expected_doc)

        self.print_section("Test 4: Source Citation")
        self.test_source_citation()

        self.print_section("Test 5: Confidence & Risk Assessment")
        self.test_confidence_and_risk()

        self.print_section("FINAL RESULTS")
        print(f"\nTests Passed: {self.passed}")
        print(f"Tests Failed: {self.failed}")
        print(f"Total: {self.passed + self.failed}")
        print(f"Success Rate: {100 * self.passed / (self.passed + self.failed):.1f}%")

        if self.failed == 0:
            print("\nSUCCESS! All tests passed.")
            print("The system is ready for production deployment.")
            print("\nNext steps:")
            print("1. Start the frontend: cd frontend-nextjs && npm run dev")
            print("2. Test in browser: http://localhost:3000")
            print("3. Submit queries and verify responses")
            return True
        else:
            print(f"\nWARNING: {self.failed} test(s) failed.")
            return False


if __name__ == "__main__":
    runner = TestRunner()
    success = runner.run_all_tests()
    exit(0 if success else 1)
