import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import time

class TestOpenCart:   

    @pytest.mark.testcase_id("TC-999")
    def test_dummy(self, custom_json_reporter):    # Add the fixture parameter here
        assert True
        # Explicitly record the test result
        #custom_json_reporter.record_result("TC-999", "Passed")