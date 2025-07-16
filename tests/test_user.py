import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import time

class TestOpenCart:
    @pytest.fixture
    def browser(self):
        # Setup - create a browser instance
        driver = webdriver.Chrome()  # You can change to Firefox, Edge, etc.
        driver.maximize_window()
        driver.get("https://demo.opencart.com.gr/")  # Change URL if your OpenCart is hosted elsewhere
        yield driver
        # Teardown - close the browser
        driver.quit()
    
    
    def test_homepage_loads_TC_001(self):       
        assert 1==2
    
    def test_product_search_TC_002(self, browser):
        """[TC-002] Test the product search functionality"""
        # Enter search term
        search_term = "phone"
        search_box = browser.find_element(By.NAME, "search")
        search_box.clear()
        search_box.send_keys(search_term)
        
        # Try different ways to submit the search
        try:
            # First try to find search button using various common selectors
            for selector in [
                "button[type='button'][class*='btn']",  # Common in newer versions
                ".btn-default",  # Used in some themes
                "button.btn",    # Generic bootstrap button
                "#search button", # Button inside search element
                "//div[@id='search']//button",  # XPath alternative
            ]:
                try:
                    # Try CSS selector first
                    if "//" not in selector:
                        search_button = browser.find_element(By.CSS_SELECTOR, selector)
                    else:
                        # If it contains //, treat as XPath
                        search_button = browser.find_element(By.XPATH, selector)
                    search_button.click()
                    break
                except NoSuchElementException:
                    continue
        except:
            # If all button selectors fail, try pressing Enter
            search_box.send_keys(Keys.RETURN)
        
        # Wait for search results page to load
        try:
            WebDriverWait(browser, 10).until(
                EC.presence_of_element_located((By.ID, "content"))
            )
            
            # Get the page source after search
            page_source = browser.page_source.lower()
            search_content = browser.find_element(By.ID, "content").text.lower()
            
            # Check if either search term is in the results or we have search results page
            assert (search_term.lower() in search_content or 
                    "search" in search_content or
                    "product" in search_content), "Search results should contain search term or product listings"
            
        except TimeoutException:
            pytest.fail("Search results did not load within the timeout period")
    
    
    def test_add_to_cart_TC_003(self, browser):
        """[TC-003] Test adding a product to the cart"""
        try:
            # First try to navigate to a product category
            category_links = browser.find_elements(By.CSS_SELECTOR, "#menu a")
            for link in category_links:
                try:
                    if link.is_displayed():
                        link.click()
                        break
                except:
                    continue
            
            # Wait for page to load
            WebDriverWait(browser, 10).until(
                EC.presence_of_element_located((By.ID, "content"))
            )
            
            # Try to find a product to click on
            product_selectors = [
                ".product-layout:first-child",
                ".product-thumb:first-child",
                ".product:first-child",
                "//div[contains(@class, 'product')]"
            ]
            
            for selector in product_selectors:
                try:
                    if "//" not in selector:
                        browser.find_element(By.CSS_SELECTOR, selector).click()
                    else:
                        browser.find_element(By.XPATH, selector).click()
                    break
                except:
                    continue
                    
            # Wait for product page to load
            WebDriverWait(browser, 10).until(
                EC.presence_of_element_located((By.ID, "product"))
            )
            
            # Get product name for verification later
            try:
                product_name = browser.find_element(By.CSS_SELECTOR, "h1").text
            except:
                product_name = "Product"  # Fallback if we can't get the name
            
            # Try to find and click the add to cart button
            cart_button_selectors = [
                "#button-cart",
                "button[id*='cart']",
                "//button[contains(@id, 'cart')]",
                "//button[contains(text(), 'Add to Cart')]"
            ]
            
            for selector in cart_button_selectors:
                try:
                    if "//" not in selector:
                        add_to_cart_button = browser.find_element(By.CSS_SELECTOR, selector)
                    else:
                        add_to_cart_button = browser.find_element(By.XPATH, selector)
                    add_to_cart_button.click()
                    break
                except:
                    continue
            
            # Wait for success message or cart update
            time.sleep(2)  # Short wait for the cart to update
            
            # Try to verify the cart was updated - either via alert or cart icon
            success = False
            try:
                # Check for success message
                alerts = browser.find_elements(By.CSS_SELECTOR, ".alert")
                for alert in alerts:
                    if "success" in alert.get_attribute("class").lower():
                        success = True
                        break
            except:
                pass
                
            if not success:
                # Check if cart has items
                try:
                    cart_total = browser.find_element(By.CSS_SELECTOR, "#cart-total")
                    assert "0 item" not in cart_total.text.lower(), "Cart should contain items"
                    success = True
                except:
                    pass
                    
            # Final assertion
            assert success, "Should have evidence that product was added to cart"
            
        except Exception as e:
            pytest.fail(f"Failed to add product to cart: {str(e)}")
    
    
    def test_user_login_TC_004(self, browser):
        """[TC-004] Test the user login functionality"""
        try:
            # Navigate to account/login page
            # First find the My Account dropdown
            account_links = [
                "#top-links a[title='My Account']",
                ".dropdown:contains('My Account')",
                "//a[contains(text(), 'My Account')]",
                "//a[contains(@title, 'My Account')]"
            ]
            
            # Try all possible selectors for My Account dropdown
            for selector in account_links:
                try:
                    if "//" not in selector:
                        my_account = browser.find_element(By.CSS_SELECTOR, selector)
                    else:
                        my_account = browser.find_element(By.XPATH, selector)
                    my_account.click()
                    break
                except:
                    continue
            
            # Small wait for dropdown to appear
            time.sleep(1)
            
            # Try to find and click Login
            login_links = [
                "a:contains('Login')",
                "//a[contains(text(), 'Login')]",
                "#top-links a[href*='login']",
                "//a[contains(@href, 'login')]"
            ]
            
            for selector in login_links:
                try:
                    if "//" not in selector:
                        login_link = browser.find_element(By.CSS_SELECTOR, selector)
                    else:
                        login_link = browser.find_element(By.XPATH, selector)
                    login_link.click()
                    break
                except:
                    continue
            
            # Alternative: Try direct navigation if dropdown approach fails
            try:
                WebDriverWait(browser, 5).until(
                    EC.presence_of_element_located((By.ID, "content"))
                )
                
                # Check if we're on login page
                if "login" not in browser.current_url:
                    browser.get("https://demo.opencart.com.gr/index.php?route=account/login")
            except:
                browser.get("https://demo.opencart.com.gr/index.php?route=account/login")
            
            # Wait for login form to load
            WebDriverWait(browser, 10).until(
                EC.presence_of_element_located((By.ID, "content"))
            )
            
            # Fill out the login form - use demo account credentials
            # Email - assuming default OpenCart demo credentials, adjust if needed
            email_field = browser.find_element(By.ID, "input-email")
            email_field.clear()
            email_field.send_keys("demo@opencart.com")  # Replace with actual test account email
            
            # Password
            password_field = browser.find_element(By.ID, "input-password")
            password_field.clear() 
            password_field.send_keys("demo1234")  # Replace with actual test account password
            
            # Submit the form
            submit_button_selectors = [
                "input[type='submit']",
                ".btn-primary",
                "button[type='submit']",
                "//input[@type='submit']",
                "//button[@type='submit']",
                "//button[contains(text(), 'Login')]",
                "//input[contains(@value, 'Login')]"
            ]
            
            for selector in submit_button_selectors:
                try:
                    if "//" not in selector:
                        submit_button = browser.find_element(By.CSS_SELECTOR, selector)
                    else:
                        submit_button = browser.find_element(By.XPATH, selector)
                    submit_button.click()
                    break
                except:
                    continue
            
            # Wait for login to complete (success means being redirected to account page)
            try:
                # Wait for page to load after form submission
                WebDriverWait(browser, 10).until(
                    EC.presence_of_element_located((By.ID, "content"))
                )
                
                # Check for login success - either by URL or page content
                success = False
                
                # Check URL for account area
                if "account" in browser.current_url and "login" not in browser.current_url:
                    success = True
                
                # Check page content for account page indicators
                if not success:
                    account_indicators = [
                        "My Account",
                        "Account Dashboard",
                        "My Orders",
                        "Logout"
                    ]
                    
                    page_content = browser.find_element(By.ID, "content").text
                    for indicator in account_indicators:
                        if indicator in page_content:
                            success = True
                            break
                
                assert success, "Login should complete successfully and redirect to account area"
                
            except TimeoutException:
                pytest.fail("Login completion page did not load within timeout period")
            
        except Exception as e:
            pytest.fail(f"Failed to complete user login: {str(e)}")
    def login(self, browser,custom_json_reporter):
        """Helper method to log in to OpenCart"""
        try:
            # Navigate to login page
            # First find the My Account dropdown
            account_links = [
                "#top-links a[title='My Account']",
                ".dropdown:contains('My Account')",
                "//a[contains(text(), 'My Account')]",
                "//a[contains(@title, 'My Account')]"
            ]
            
            # Try all possible selectors for My Account dropdown
            for selector in account_links:
                try:
                    if "//" not in selector:
                        my_account = browser.find_element(By.CSS_SELECTOR, selector)
                    else:
                        my_account = browser.find_element(By.XPATH, selector)
                    my_account.click()
                    break
                except:
                    continue
            
            # Small wait for dropdown to appear
            time.sleep(1)
            
            # Try to find and click Login
            login_links = [
                "a:contains('Login')",
                "//a[contains(text(), 'Login')]",
                "#top-links a[href*='login']",
                "//a[contains(@href, 'login')]"
            ]
            
            for selector in login_links:
                try:
                    if "//" not in selector:
                        login_link = browser.find_element(By.CSS_SELECTOR, selector)
                    else:
                        login_link = browser.find_element(By.XPATH, selector)
                    login_link.click()
                    break
                except:
                    continue
            
            # Alternative: Try direct navigation if dropdown approach fails
            try:
                WebDriverWait(browser, 5).until(
                    EC.presence_of_element_located((By.ID, "content"))
                )
                
                # Check if we're on login page
                if "login" not in browser.current_url:
                    browser.get("https://demo.opencart.com.gr/index.php?route=account/login")
            except:
                browser.get("https://demo.opencart.com.gr/index.php?route=account/login")
            
            # Wait for login form to load
            WebDriverWait(browser, 10).until(
                EC.presence_of_element_located((By.ID, "content"))
            )
            
            # Fill out the login form - use demo account credentials
            # Email - assuming default OpenCart demo credentials, adjust if needed
            email_field = browser.find_element(By.ID, "input-email")
            email_field.clear()
            email_field.send_keys("demo@opencart.com")  # Replace with actual test account email
            
            # Password
            password_field = browser.find_element(By.ID, "input-password")
            password_field.clear() 
            password_field.send_keys("demo1234")  # Replace with actual test account password
            
            # Submit the form
            submit_button_selectors = [
                "input[type='submit']",
                ".btn-primary",
                "button[type='submit']",
                "//input[@type='submit']",
                "//button[@type='submit']",
                "//button[contains(text(), 'Login')]",
                "//input[contains(@value, 'Login')]"
            ]
            
            for selector in submit_button_selectors:
                try:
                    if "//" not in selector:
                        submit_button = browser.find_element(By.CSS_SELECTOR, selector)
                    else:
                        submit_button = browser.find_element(By.XPATH, selector)
                    submit_button.click()
                    break
                except:
                    continue
            
            # Wait for login to complete (success means being redirected to account page)
            try:
                # Wait for page to load after form submission
                WebDriverWait(browser, 10).until(
                    EC.presence_of_element_located((By.ID, "content"))
                )
                
                # Check for login success - either by URL or page content
                success = False
                
                # Check URL for account area
                if "account" in browser.current_url and "login" not in browser.current_url:
                    success = True
                
                # Check page content for account page indicators
                if not success:
                    account_indicators = [
                        "My Account",
                        "Account Dashboard",
                        "My Orders",
                        "Logout"
                    ]
                    
                    page_content = browser.find_element(By.ID, "content").text
                    for indicator in account_indicators:
                        if indicator in page_content:
                            success = True
                            break
                
                assert success, "Login should complete successfully and redirect to account area"
                
                # Return to homepage
                browser.get("https://demo.opencart.com.gr/")
                
            except TimeoutException:
                pytest.fail("Login completion page did not load within timeout period")
            
        except Exception as e:
            pytest.fail(f"Failed to complete user login: {str(e)}")
        
   
    def test_wishlist_functionality_TC_005(self, browser):
        """[TC-005] Test adding a product to the wishlist"""
        try:
            # First, login to the account
            self.login(browser)
            
            # Then navigate to a product
            # Try to find a featured product on homepage
            product_selectors = [
                ".product-layout",
                ".product-thumb",
                "//div[contains(@class, 'product-layout')]",
                "//div[contains(@class, 'product-thumb')]"
            ]
            
            product_found = False
            for selector in product_selectors:
                try:
                    products = browser.find_elements(By.XPATH if "//" in selector else By.CSS_SELECTOR, selector)
                    if products and len(products) > 0:
                        # Click the first product
                        products[0].click()
                        product_found = True
                        break
                except:
                    continue
            
            # If no product found on homepage, try to browse a category
            if not product_found:
                try:
                    # Try to click on a category
                    categories = browser.find_elements(By.CSS_SELECTOR, "#menu a")
                    for category in categories:
                        if category.is_displayed():
                            category.click()
                            # Try to find a product in category page
                            WebDriverWait(browser, 10).until(
                                EC.presence_of_element_located((By.ID, "content"))
                            )
                            for selector in product_selectors:
                                try:
                                    products = browser.find_elements(By.XPATH if "//" in selector else By.CSS_SELECTOR, selector)
                                    if products and len(products) > 0:
                                        products[0].click()
                                        product_found = True
                                        break
                                except:
                                    continue
                            if product_found:
                                break
                except:
                    # If all fails, try direct product URL
                    browser.get("https://demo.opencart.com.gr/index.php?route=product/product&product_id=43")
                    product_found = True
            
            # Wait for product page to load
            WebDriverWait(browser, 10).until(
                EC.presence_of_element_located((By.ID, "product"))
            )
            
            # Get product name for verification
            try:
                product_name = browser.find_element(By.CSS_SELECTOR, "h1").text
            except:
                product_name = "Product"  # Fallback
            
            # Try to find and click add to wishlist button
            wishlist_button_selectors = [
                "button[data-original-title='Add to Wish List']",
                "button[title='Add to Wish List']",
                ".fa-heart",
                "button[onclick*='wishlist']",
                "//button[contains(@onclick, 'wishlist')]",
                "//button[contains(@data-original-title, 'Wish List')]",
                "//button[contains(@title, 'Wish List')]",
                "//i[contains(@class, 'fa-heart')]/.."
            ]
            
            wishlist_clicked = False
            for selector in wishlist_button_selectors:
                try:
                    if "//" not in selector:
                        wishlist_button = browser.find_element(By.CSS_SELECTOR, selector)
                    else:
                        wishlist_button = browser.find_element(By.XPATH, selector)
                    wishlist_button.click()
                    wishlist_clicked = True
                    break
                except:
                    continue
            
            assert wishlist_clicked, "Should be able to click wishlist button"
            
            # Wait for success message
            time.sleep(2)
            
            # Check for success message
            success = False
            try:
                alerts = browser.find_elements(By.CSS_SELECTOR, ".alert")
                for alert in alerts:
                    alert_text = alert.text.lower()
                    if "success" in alert.get_attribute("class").lower() and "wish list" in alert_text:
                        success = True
                        break
            except:
                pass
            
            # If no success message, try to navigate to wishlist to verify
            if not success:
                # Wait a moment for any animations/processes to complete
                time.sleep(2)
                
                # Try to navigate to wishlist
                wishlist_page_selectors = [
                    "a[title='Wish List']",
                    "#wishlist-total",
                    "//a[contains(@title, 'Wish List')]",
                    "//a[contains(text(), 'Wish List')]"
                ]
                
                wishlist_nav_clicked = False
                for selector in wishlist_page_selectors:
                    try:
                        if "//" not in selector:
                            wishlist_link = browser.find_element(By.CSS_SELECTOR, selector)
                        else:
                            wishlist_link = browser.find_element(By.XPATH, selector)
                        wishlist_link.click()
                        wishlist_nav_clicked = True
                        break
                    except:
                        continue
                
                # If navigation didn't work, try direct URL
                if not wishlist_nav_clicked:
                    browser.get("https://demo.opencart.com.gr/index.php?route=account/wishlist")
                
                # Wait for wishlist page to load
                try:
                    WebDriverWait(browser, 10).until(
                        EC.presence_of_element_located((By.ID, "content"))
                    )
                    
                    # Check if wishlist contains our product
                    page_content = browser.find_element(By.ID, "content").text
                    if "wish list" in page_content.lower() and (product_name in page_content or "product" in page_content.lower()):
                        success = True
                except:
                    pass
            
            assert success, "Product should be added to wishlist successfully"
                
        except Exception as e:
            pytest.fail(f"Failed to add product to wishlist: {str(e)}")

    
    def test_remove_from_wishlistTC_006(self, browser):
        """[TC-006] Test removing a product from the wishlist"""
        try:
            # First add a product to wishlist
            self.test_wishlist_functionality(browser)
            
            # Navigate to wishlist page
            wishlist_page_selectors = [
                "a[title='Wish List']",
                "#wishlist-total",
                "//a[contains(@title, 'Wish List')]",
                "//a[contains(text(), 'Wish List')]"
            ]
            
            wishlist_nav_clicked = False
            for selector in wishlist_page_selectors:
                try:
                    if "//" not in selector:
                        wishlist_link = browser.find_element(By.CSS_SELECTOR, selector)
                    else:
                        wishlist_link = browser.find_element(By.XPATH, selector)
                    wishlist_link.click()
                    wishlist_nav_clicked = True
                    break
                except:
                    continue
            
            # If navigation didn't work, try direct URL
            if not wishlist_nav_clicked:
                browser.get("https://demo.opencart.com.gr/index.php?route=account/wishlist")
            
            # Wait for wishlist page to load
            WebDriverWait(browser, 10).until(
                EC.presence_of_element_located((By.ID, "content"))
            )
            
            # Get the number of products in wishlist before removal
            products_before = 0
            try:
                # Look for table rows in wishlist
                wishlist_rows = browser.find_elements(By.CSS_SELECTOR, ".table-responsive tr")
                # Subtract header row if present
                products_before = len(wishlist_rows) - 1 if len(wishlist_rows) > 0 else 0
            except:
                # Alternative method if table structure is different
                try:
                    wishlist_items = browser.find_elements(By.CSS_SELECTOR, ".product-layout")
                    products_before = len(wishlist_items)
                except:
                    # Default to 1 if we can't determine the count
                    products_before = 1
            
            # Try to find and click remove button
            remove_button_selectors = [
                "a[data-original-title='Remove']",
                "a[title='Remove']",
                ".fa-times",
                "button[onclick*='remove']",
                "//a[contains(@onclick, 'remove')]",
                "//i[contains(@class, 'fa-times')]/.."
            ]
            
            remove_clicked = False
            for selector in remove_button_selectors:
                try:
                    if "//" not in selector:
                        remove_buttons = browser.find_elements(By.CSS_SELECTOR, selector)
                    else:
                        remove_buttons = browser.find_elements(By.XPATH, selector)
                    
                    if remove_buttons and len(remove_buttons) > 0:
                        # Click the first remove button
                        remove_buttons[0].click()
                        remove_clicked = True
                        break
                except:
                    continue
            
            assert remove_clicked, "Should be able to click remove button"
            
            # Wait for page to refresh
            time.sleep(2)
            
            # Verify product was removed
            # Option 1: Check for success message
            success = False
            try:
                alerts = browser.find_elements(By.CSS_SELECTOR, ".alert")
                for alert in alerts:
                    alert_text = alert.text.lower()
                    if "success" in alert.get_attribute("class").lower() and "removed" in alert_text:
                        success = True
                        break
            except:
                pass
            
            # Option 2: Check if number of products decreased
            if not success:
                try:
                    # Look for table rows in wishlist
                    wishlist_rows = browser.find_elements(By.CSS_SELECTOR, ".table-responsive tr")
                    # Subtract header row if present
                    products_after = len(wishlist_rows) - 1 if len(wishlist_rows) > 0 else 0
                    
                    if products_after < products_before:
                        success = True
                except:
                    # Alternative method if table structure is different
                    try:
                        wishlist_items = browser.find_elements(By.CSS_SELECTOR, ".product-layout")
                        products_after = len(wishlist_items)
                        
                        if products_after < products_before:
                            success = True
                    except:
                        pass
            
            # Option 3: Check for "empty wishlist" message
            if not success:
                try:
                    page_content = browser.find_element(By.ID, "content").text.lower()
                    if "empty" in page_content and "wishlist" in page_content:
                        success = True
                except:
                    pass
            
            assert success, "Product should be removed from wishlist successfully"
                
        except Exception as e:
            pytest.fail(f"Failed to remove product from wishlist: {str(e)}")