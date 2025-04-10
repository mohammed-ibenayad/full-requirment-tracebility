# simple_reporter_plugin.py
import os
import pytest
import json
from datetime import datetime

class SimpleJSONReporter:
    def __init__(self, json_file="open-cart-test-cases.json", executor="Pytest"):
        self.json_file = json_file
        self.executor = executor
        self.test_results = {}
        self.test_cases = []
        self.test_case_map = {}
        
        # Load test cases
        try:
            with open(self.json_file, 'r') as f:
                self.test_cases = json.load(f)
            
            self.test_case_map = {tc['id']: i for i, tc in enumerate(self.test_cases)}
            print(f"\nLoaded {len(self.test_cases)} test cases from {self.json_file}")
        except Exception as e:
            print(f"\nWarning: Could not load test cases from {self.json_file}: {e}")
    
    def record_result(self, test_id, status):
        self.test_results[test_id] = status
        print(f"\nRecorded test result: {test_id} -> {status}")
    
    def save_results(self):
        if not self.test_results or not self.test_cases:
            return
        
        updates = 0
        for test_id, status in self.test_results.items():
            if test_id in self.test_case_map:
                idx = self.test_case_map[test_id]
                self.test_cases[idx]['status'] = status
                self.test_cases[idx]['lastExecuted'] = datetime.now().isoformat()
                if 'executedBy' in self.test_cases[idx]:
                    self.test_cases[idx]['executedBy'] = self.executor
                updates += 1
        
        if updates > 0:
            try:
                with open(self.json_file, 'w') as f:
                    json.dump(self.test_cases, f, indent=2)
                print(f"\nUpdated {updates} test cases in {self.json_file}")
            except Exception as e:
                print(f"\nError saving results: {e}")

# Create a pytest fixture for the reporter
@pytest.fixture(scope="session")
def json_reporter(request):
    """Fixture that provides access to the JSON reporter"""
    # Get values from command line options if available
    json_file = getattr(request.config.option, 'json_file', 'open-cart-test-cases.json')
    executor = getattr(request.config.option, 'json_executor', 'Pytest')
    
    reporter = SimpleJSONReporter(json_file, executor)
    yield reporter
    
    # Save results at the end of the session
    reporter.save_results()

# Add pytest hooks to collect test IDs
@pytest.hookimpl(tryfirst=True)
def pytest_runtest_setup(item, json_reporter):
    """Extract test case ID from the test"""
    marker = item.get_closest_marker("testcase_id")
    if marker and marker.args:
        item.test_case_id = marker.args[0]

@pytest.hookimpl(trylast=True)
def pytest_runtest_makereport(item, call, json_reporter):
    """Record test results"""
    if call.when == "call" and hasattr(item, "test_case_id"):
        status = "Passed" if call.excinfo is None else "Failed"
        json_reporter.record_result(item.test_case_id, status)

# Register command line options
def pytest_addoption(parser):
    group = parser.getgroup("json_reporter")
    group.addoption(
        "--json-file",
        help="JSON file to update with test results",
        default="open-cart-test-cases.json"
    )
    group.addoption(
        "--json-executor",
        help="Name of the test executor",
        default="Pytest"
    )