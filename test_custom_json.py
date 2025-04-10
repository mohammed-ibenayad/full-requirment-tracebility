# test_custom_json.py
import pytest

@pytest.mark.testcase_id("TC-999")
def test_with_custom_reporter(custom_json_reporter):
    """Test with our custom JSON reporter"""
    print("\nRunning test with TC-999")
    assert True