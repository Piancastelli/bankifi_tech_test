import logging
import unittest
from time import sleep

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException


class TestLoginPage(unittest.TestCase):
    """Test class for the login page"""
    @classmethod
    def setUpClass(cls):
        cls.logger = logging.Logger("LoginPage")
        cls.logger.setLevel(logging.INFO)

        cls.base_address = "https://www.saucedemo.com"
        cls.valid_password = "secret_sauce"
        cls.delay = 1

    def setUp(self):
        self.driver = webdriver.Firefox()  # Restart firefox before every test to ensure a clean state
        self.driver.get(self.base_address)

        self.username_field = self.driver.find_element_by_id("user-name")
        self.username_field.clear()
        self.password_field = self.driver.find_element_by_id("password")
        self.password_field.clear()
        self.addCleanup(self.driver.close)

    def wait_for_page_id(self, verification_id):
        """Method for waiting for the page to load based on presence of an element found by ID"""
        try:
            WebDriverWait(self.driver, self.delay).until(EC.presence_of_element_located((By.ID, verification_id)))

        except TimeoutException:
            self.fail("Page should contain element with id '{}' but does not".format(verification_id))

    def wait_for_page_class(self, verification_class):
        """Method for waiting for the page to load based on presence of an element found by class"""
        try:
            WebDriverWait(self.driver, self.delay).\
                          until(EC.presence_of_element_located((By.CLASS_NAME, verification_class)))

        except TimeoutException:
            self.fail("Page should contain element with class '{}' but does not".format(verification_class))


    def url_assert(self, endpoint):
        """Method to assert that the URL of the current page is what is expected"""
        assert self.driver.current_url.endswith(endpoint),\
               "URL is {}\nShould end with {}".format(self.driver.current_url, endpoint)

    def test_valid_credentials_return(self):
        """Test that it is possible to log in using valid credentials, submit using return key"""
        self.username_field.send_keys("standard_user")
        self.password_field.send_keys(self.valid_password)
        self.password_field.send_keys(Keys.RETURN)
        self.wait_for_page_id("searchbox_container")

        self.url_assert("inventory.html")

    def test_locked_out_user_return(self):
        """Test that attempting to log in with 'locked_out_user' fails, submit using return key"""
        self.username_field.send_keys("locked_out_user")
        self.password_field.send_keys(self.valid_password)
        self.password_field.send_keys(Keys.RETURN)
        self.wait_for_page_class("error-button")

        # Want to make sure we're not on the page after successful login
        assert not self.driver.current_url.endswith("inventory.html"),\
               "URL is {}\nShould not end with 'inventory.html'".format(self.driver.current_url)

        # Check for appropriate error message
        error_msg_text = self.driver.find_element_by_xpath("//div[@class='login-box']/form/h3").text
        assert "this user has been locked out" in error_msg_text,\
               "Did not find appropriate error message, found {}".format(error_msg_text)


    def test_valid_credentials_login_button(self):
        """Test that it is possible to log in using valid credentials, submit using LOGIN button"""
        self.username_field.send_keys("standard_user")
        self.password_field.send_keys(self.valid_password)
        self.driver.find_element_by_class_name("btn_action").click()
        self.wait_for_page_id("searchbox_container")

        # Check the URL is as expected
        assert self.driver.current_url.endswith("inventory.html"),\
               "URL is {}\nShould end with 'inventory.html'".format(self.driver.current_url)

    def test_all_the_way_through_single_item(self):
        """Log in, add one item to the basket, proceed to checkout, then checkout"""
        self.username_field.send_keys("standard_user")
        self.password_field.send_keys(self.valid_password)
        self.driver.find_element_by_class_name("btn_action").click()
        self.wait_for_page_id("searchbox_container")
        # Logged in at this point

        self.driver.find_element_by_class_name("btn_primary").click()  # Will always click the first Add to cart button
        assert self.driver.find_element_by_class_name("btn_secondary").text == u"REMOVE"  # Want to be sure it added the item
        assert self.driver.find_element_by_class_name("fa-layers-counting").text == 1

        self.driver.find_element_by_class_name("shopping_cart_link").click()
        self.url_assert("cart.html")
        self.wait_for_page_class("cart_list")
        try:
            self.driver.find_element_by_class_name("cart_item")
        except NoSuchElementException:
            self.fail("There were no items in the cart when there was supposed to be one")

        self.driver.find_element_by_class_name("checkout_button").click()
        self.wait_for_page_id("checkout_info_container")
        self.url_assert("checkout-step-one.html")
        self.driver.find_element_by_id("first-name").send_keys("Firstname")
        self.driver.find_element_by_id("last-name").send_keys("Lastname")
        self.driver.find_element_by_id("postal-code").send_keys("postal code")

        self.driver.find_element_by_class_name("cart_button").click()
        self.wait_for_page_id("checkout_summary_container")
        self.url_assert("checkout-step-two.html")

        self.driver.find_element_by_class_name("cart_button").click()
        self.wait_for_page_id("checkout_complete_container")
        self.url_assert("checkout-complete.html")


        header_text = self.driver.find_element_by_class_name("complete-header").text
        expected = u"THANK YOU FOR YOUR ORDER"
        assert header_text == expected, "Expected: {}\nGot: {}".format(expected, header_text)