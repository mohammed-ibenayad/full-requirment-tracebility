"""
Pytest plugin for test result reporting to JSON

This plugin automatically updates test case statuses in a JSON file.
It can be used with any test framework, not specific to OpenCart.
"""

import os
import re
import pytest
import json
from datetime import datetime


# Default test cases JSON file path
DEFAULT_JSON_PATH = os.environ.get('TEST_CASES_JSON', 'test-cases.json')
# Default executor name
DEFAULT_EXECUTOR = os.environ.get('TEST_EXECUTOR', 'Pytest')


def pytest_addoption(parser):
    """Add plugin options to pytest"""
    group = parser.getgroup('json_reporter', 'JSON test reporting')
    group.addoption(
        '--json-file',
        action='store',
        dest='json_file',
        default=DEFAULT_JSON_PATH,
        help='Path to the test cases JSON file'
    )
    group.addoption(
        '--json-executor',
        action='store',
        dest='json_executor',
        default=DEFAULT_EXECUTOR,
        help='Name of the test executor to record in results'
    )
    group.addoption(
        '--update-json',
        action='store_true',
        dest='update_json',
        default=False,
        help='Enable updating test case statuses in the JSON file'
    )


@pytest.hookimpl(trylast=True)
def pytest_configure(config):
    """Set up the plugin"""
    if config.getoption('update_json'):
        # Register the plugin
        plugin = JSONReportPlugin(config)
        config.pluginmanager.register(plugin, 'json-report')
        

class JSONReportPlugin:
    """Plugin to update test cases JSON with test results"""
    
    def __init__(self, config):
        self.config = config
        self.json_path = config.getoption('json_file')
        self.executor = config.getoption('json_executor')
        self.test_results = {}
        self.test_case_map = {}
        
        # Load test cases from JSON
        self._load_test_cases()
        
        print(f"\nJSON test reporting enabled:")
        print(f"  JSON file: {self.json_path}")
        print(f"  Executor: {self.executor}")
        
    def _load_test_cases(self):
        """Load test cases from the JSON file"""
        try:
            with open(self.json_path, 'r') as f:
                self.test_cases = json.load(f)
                
            # Create a map of test IDs to indices for quick lookup
            self.test_case_map = {tc['id']: i for i, tc in enumerate(self.test_cases)}
            
            print(f"\nLoaded {len(self.test_cases)} test cases from {self.json_path}")
            
        except Exception as e:
            print(f"\nWarning: Could not load test cases from {self.json_path}: {e}")
            self.test_cases = []
            
    def _extract_test_id(self, nodeid):
        """
        Extract the test case ID from a test node ID
        
        Looks for patterns like:
        - @pytest.mark.testcase_id("TC-001")
        - [TC-001] in the docstring
        - test_*_001 -> TC-001
        """
        # Check for testcase_id marker in item
        for item in self.config.hook.pytest_collection_modifyitems.get_hookimpls():
            module = item.plugin.__module__
            if hasattr(module, 'testcase_id'):
                return module.testcase_id
                
        # Extract the function name from the nodeid (path::class::function)
        parts = nodeid.split('::')
        func_name = parts[-1] if len(parts) > 1 else nodeid
        
        # Look for common patterns in the function name
        patterns = [
            r'test[-_](\w+)[-_](\d+)',  # e.g., test_homepage_001 -> TC-001
            r'\[([-\w]+[-_]?\d+)\]',    # e.g., [TC-001] in docstring
            r'([-\w]+)[-_]?(\d+)',      # e.g., TC-001 or TC_001 in name
        ]
        
        for pattern in patterns:
            match = re.search(pattern, nodeid, re.IGNORECASE)
            if match:
                # If the pattern includes a prefix and number, combine them
                if len(match.groups()) > 1 and match.group(1) and match.group(2):
                    prefix = match.group(1).upper()
                    number = match.group(2).zfill(3)
                    return f"{prefix}-{number}"
                # If it's already a full ID like TC-001
                elif len(match.groups()) == 1:
                    return match.group(1)
        
        return None
        
    def _update_test_case(self, test_id, status):
        """Update a test case status in the JSON file"""
        if not test_id or not self.test_cases:
            return False
            
        if test_id not in self.test_case_map:
            print(f"Warning: Test case {test_id} not found in JSON file")
            return False
            
        # Update the test case
        index = self.test_case_map[test_id]
        self.test_cases[index]['status'] = status
        self.test_cases[index]['lastExecuted'] = datetime.now().isoformat()
        
        if 'executedBy' in self.test_cases[index]:
            self.test_cases[index]['executedBy'] = self.executor
        
        return True
        
    def _save_test_cases(self):
        """Save test cases back to the JSON file"""
        if not self.test_cases:
            return
            
        try:
            with open(self.json_path, 'w') as f:
                json.dump(self.test_cases, f, indent=2)
                
            print(f"\nUpdated {len(self.test_results)} test case results in {self.json_path}")
            
        except Exception as e:
            print(f"\nError saving test cases to {self.json_path}: {e}")
            
    @pytest.hookimpl(tryfirst=True)
    def pytest_runtest_setup(self, item):
        """Called before each test is run"""
        # Try to get the test case ID from marker
        marker = item.get_closest_marker('testcase_id')
        if marker:
            test_id = marker.args[0] if marker.args else None
            if test_id:
                item.test_case_id = test_id
                return
                
        # Extract the test case ID from the nodeid
        test_id = self._extract_test_id(item.nodeid)
        if test_id:
            item.test_case_id = test_id
        
    @pytest.hookimpl(trylast=True)
    def pytest_runtest_makereport(self, item, call):
        """Called when a test completes, with the result"""
        if call.when == 'call':  # Only process the test result after it's completed
            if not hasattr(item, 'test_case_id'):
                # Try to extract test ID one more time
                test_id = self._extract_test_id(item.nodeid)
                if not test_id:
                    return
                item.test_case_id = test_id
                
            # Determine the test status
            if call.excinfo is None:
                status = 'Passed'
            elif call.excinfo.typename == 'Skipped':
                status = 'Skipped'
            else:
                status = 'Failed'
                
            # Store the result
            self.test_results[item.test_case_id] = status
            print(f"\nTest {item.nodeid} -> {item.test_case_id}: {status}")
            
    @pytest.hookimpl(trylast=True)
    def pytest_sessionfinish(self, session):
        """Called after all tests are completed"""
        if not self.test_results:
            print("\nNo test results collected")
            return
            
        # Update each test case
        update_count = 0
        for test_id, status in self.test_results.items():
            if self._update_test_case(test_id, status):
                update_count += 1
                
        print(f"\nUpdated {update_count} test case statuses")
        
        # Save the updated test cases
        self._save_test_cases()


# Register the marker for test case IDs
def pytest_configure(config):
    config.addinivalue_line(
        'markers',
        'testcase_id(id): mark a test with a test case ID'
    )