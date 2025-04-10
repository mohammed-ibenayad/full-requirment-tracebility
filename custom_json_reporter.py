"""
Custom JSON reporter for test results
"""

import os
import pytest
import json
from datetime import datetime


class CustomJSONReporter:
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
        print(f"Current test results: {self.test_results}")  # Debug print
    
    def save_results(self):
        print(f"\nAttempting to save results: {len(self.test_results)} results")
        if not self.test_results or not self.test_cases:
            print("\nNo results or test cases to save")
            return
        
        updates = 0
        for test_id, status in self.test_results.items():
            print(f"Processing test result for {test_id}")  # Debug print
            if test_id in self.test_case_map:
                idx = self.test_case_map[test_id]
                print(f"Found test case at index {idx}")  # Debug print
                self.test_cases[idx]['status'] = status
                self.test_cases[idx]['lastExecuted'] = datetime.now().isoformat()
                if 'executedBy' in self.test_cases[idx]:
                    self.test_cases[idx]['executedBy'] = self.executor
                updates += 1
            else:
                print(f"WARNING: Test ID {test_id} not found in test case map")
        
        if updates > 0:
            try:
                print(f"Writing {updates} updates to {self.json_file}")  # Debug print
                with open(self.json_file, 'w') as f:
                    json.dump(self.test_cases, f, indent=2)
                print(f"\nUpdated {updates} test cases in {self.json_file}")
            except Exception as e:
                print(f"\nError saving results: {e}")
                # Print more details about the error
                import traceback
                traceback.print_exc()


# Global reporter instance
_reporter = None

def get_reporter(json_file="open-cart-test-cases.json", executor="Pytest"):
    """Get or create the reporter instance"""
    global _reporter
    if _reporter is None:
        # Create the JSON file if it doesn't exist
        if not os.path.exists(json_file):
            print(f"\nCreating new JSON file: {json_file}")
            with open(json_file, "w") as f:
                json.dump([
                    {
                        "id": "TC-999",
                        "name": "Test Dummy",
                        "description": "Test Dummy",
                        "status": "Not Run",
                        "lastExecuted": "",
                        "executedBy": ""
                    }
                ], f, indent=2)
        
        _reporter = CustomJSONReporter(json_file, executor)
    return _reporter


# Test case ID extraction function
def get_test_id(item):
    """Extract the test case ID from a pytest item"""
    # First check for the testcase_id marker
    marker = item.get_closest_marker("testcase_id")
    if marker and marker.args:
        print(f"\nFound test ID from marker: {marker.args[0]}")  # Debug print
        return marker.args[0]
    print(f"\nNo test ID found for {item.nodeid}")  # Debug print
    return None


# Fixture to use in tests
@pytest.fixture(scope="function")
def custom_json_reporter(request):
    """Fixture that provides the JSON reporter in tests"""
    # Get options from request
    config = request.config
    json_file = config.getoption("--custom-json-file", "open-cart-test-cases.json")
    executor = config.getoption("--custom-executor", "Pytest")
    
    # Get the reporter
    reporter = get_reporter(json_file, executor)
    
    # Record test ID and result after test completes
    test_id = get_test_id(request.node)
    
    yield reporter
    
    # Record result after test completes
    if test_id:
        # Get result by checking if the test passed
        result = "Passed"
        if hasattr(request.node, 'rep_call') and request.node.rep_call.failed:
            result = "Failed"
        elif hasattr(request.node, 'rep_setup') and request.node.rep_setup.failed:
            result = "Failed"
        
        reporter.record_result(test_id, result)


# Add a hook to store test results
@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()
    
    if report.when == "call":
        item.rep_call = report
        # Debug print
        test_id = get_test_id(item)
        if test_id:
            print(f"\nDetected test ID in makereport: {test_id}")
            print(f"Test result: {report.outcome}")
    elif report.when == "setup":
        item.rep_setup = report


# Register our options
def pytest_addoption(parser):
    """Add custom JSON reporter options"""
    group = parser.getgroup("custom_json_reporter", "Custom JSON Test Reporting")
    group.addoption(
        "--custom-json-file",
        action="store",
        dest="custom_json_file",
        default="open-cart-test-cases.json",
        help="JSON file to update with test results"
    )
    group.addoption(
        "--custom-executor",
        action="store",
        dest="custom_executor",
        default="Pytest",
        help="Name of the test executor"
    )
    group.addoption(
        "--save-custom-json",
        action="store_true",
        dest="save_custom_json",
        default=False,
        help="Enable saving results to JSON file"
    )


# Save results at the end of the session
@pytest.hookimpl(trylast=True)
def pytest_sessionfinish(session):
    """Save all test results at the end of the test session"""
    if session.config.getoption("--save-custom-json", False):
        # Use explicitly configured file and executor names
        json_file = session.config.getoption("--custom-json-file", "open-cart-test-cases.json")
        executor = session.config.getoption("--custom-executor", "Pytest")
        reporter = get_reporter(json_file, executor)
        reporter.save_results()
        print("\nCustom JSON results saved")