import logging
from random import sample
from time import sleep
import unittest

from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class TestLoginPage(unittest.TestCase):
    """Test class for the login page"""
    @classmethod
    def setUpClass(cls):
        cls.logger = logging.Logger("LoginPage")
        cls.logger.setLevel(logging.INFO)

        cls.base_address = "https://www.saucedemo.com"
        cls.valid_password = "secret_sauce"
        cls.known_users = ["standard_user", "locked_out_user",
                           "problem_user", "performance_glitch_user"]
        cls.delay = 1

    def setUp(self):
        self.driver = webdriver.Firefox()  # Restart firefox before every test to ensure a clean state
        self.addCleanup(self.driver.close)

    def login_page_setup(self):
        """Setup method for tests that start on the login page"""
        self.driver.get(self.base_address + "/index.html")

        self.username_field = self.driver.find_element_by_id("user-name")
        self.username_field.clear()
        self.password_field = self.driver.find_element_by_id("password")
        self.password_field.clear()

    def wait_for_page_by_id(self, verification_id):
        """Method for waiting for the page to load based on presence of an element found by ID"""
        try:
            WebDriverWait(self.driver, self.delay).until(EC.presence_of_element_located((By.ID, verification_id)))

        except TimeoutException:
            self.fail("Page should contain element with id '{}' but does not".format(verification_id))

    def wait_for_page_by_class(self, verification_class):
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

    def complete_login_page(self, user):
        """Takes a user and attempts to log them in with the valid password"""
        assert user in self.known_users, "{} not a known user, choose from {}".format(user, self.known_users)

        self.username_field.send_keys(user)
        self.password_field.send_keys(self.valid_password)
        self.driver.find_element_by_class_name("btn_action").click()

    def complete_checkout_step_one(self):
        """Fill in all the fields on the first checkout page and submit the form"""
        self.driver.find_element_by_id("first-name").send_keys("Firstname")
        self.driver.find_element_by_id("last-name").send_keys("Lastname")
        self.driver.find_element_by_id("postal-code").send_keys("postal code")
        self.driver.find_element_by_class_name("cart_button").click()

#######################################################################################################################
# Login page tests
#######################################################################################################################

    def test_valid_credentials_return(self):
        """Test that it is possible to log in using valid credentials, submit using return key"""
        self.login_page_setup()

        self.username_field.send_keys("standard_user")
        self.password_field.send_keys(self.valid_password)
        self.password_field.send_keys(Keys.RETURN)
        self.wait_for_page_by_id("searchbox_container")

        self.url_assert("inventory.html")

    def test_locked_out_user_return(self):
        """Test that attempting to log in with 'locked_out_user' fails, submit using return key"""
        self.login_page_setup()

        self.username_field.send_keys("locked_out_user")
        self.password_field.send_keys(self.valid_password)
        self.password_field.send_keys(Keys.RETURN)
        self.wait_for_page_by_class("error-button")

        # Want to make sure we're not on the page after successful login
        self.url_assert("index.html")
        # Check for appropriate error message
        error_msg_text = self.driver.find_element_by_xpath("//div[@class='login-box']/form/h3").text
        assert "user has been locked out" in error_msg_text,\
               "Did not find appropriate error message, found {}".format(error_msg_text)


    def test_valid_credentials_login_button(self):
        """Test that it is possible to log in using valid credentials, submit using LOGIN button"""
        self.login_page_setup()

        self.username_field.send_keys("standard_user")
        self.password_field.send_keys(self.valid_password)
        self.driver.find_element_by_class_name("btn_action").click()
        self.wait_for_page_by_id("searchbox_container")

        # Check the URL is as expected
        self.url_assert("inventory.html")

    def test_locked_out_user_login_button(self):
        """Test that attempting to log in with 'locked_out_user' fails, submit using LOGIN button"""
        self.login_page_setup()

        self.username_field.send_keys("locked_out_user")
        self.password_field.send_keys(self.valid_password)
        self.driver.find_element_by_class_name("btn_action").click()
        self.wait_for_page_by_class("error-button")

        # Want to make sure we're not on the page after successful login
        self.url_assert("index.html")
        # Check for appropriate error message
        error_msg_text = self.driver.find_element_by_xpath("//div[@class='login-box']/form/h3").text
        assert "user has been locked out" in error_msg_text,\
               "Did not find appropriate error message, found {}".format(error_msg_text)

#######################################################################################################################
# End to end tests
#######################################################################################################################

    def test_all_the_way_through_single_item(self):
        """Log in, add one item to the basket, proceed to checkout, then checkout"""
        self.login_page_setup()
        self.complete_login_page("standard_user")
        self.wait_for_page_by_id("searchbox_container")
        self.url_assert("inventory.html")
        # Logged in at this point - Inventory page

        # Always finds first element in the list
        element_to_add = self.driver.find_element_by_class_name("inventory_item")
        item_name = element_to_add.find_element_by_class_name("inventory_item_name").text
        element_button = element_to_add.find_element_by_xpath(".//div[@class='pricebar']/button")

        element_button.click()
        # Want to be sure it added the item
        assert element_button.text == u"REMOVE",\
               "Expected button to say 'REMOVE', actually said {}".format(element_button.text)
        
        item_count = self.driver.find_element_by_class_name("fa-layers-counter").text
        assert item_count == u"1", "Expected item count to be 1, was actually {}".format(item_count)

        # Go to next page - Cart
        self.driver.find_element_by_class_name("shopping_cart_link").click()
        self.wait_for_page_by_class("cart_list")
        self.url_assert("cart.html")
        try:
            # Check the item we added is in the cart
            self.driver.find_element_by_class_name("cart_item")
        except NoSuchElementException:
            self.fail("There were no items in the cart, expected one")

        # Check the item in cart is the item we added
        inventory_item_name = self.driver.find_element_by_class_name("inventory_item_name").text
        assert item_name == inventory_item_name,\
               "Expected {} to be in the cart, but got {}".format(item_name, inventory_item_name)

        # Go to next page - Checkout step one
        self.driver.find_element_by_class_name("checkout_button").click()
        self.wait_for_page_by_id("checkout_info_container")
        self.url_assert("checkout-step-one.html")
        self.complete_checkout_step_one()

        # Go to next page
        self.wait_for_page_by_id("checkout_summary_container")
        self.url_assert("checkout-step-two.html")
        checkout_cart_list = [item.text for item in self.driver.find_elements_by_class_name("inventory_item_name")]
        assert [item_name] == checkout_cart_list,\
               "Expected cart to be {} but got {}".format([item_name], checkout_cart_list)

        # Go to next page
        self.driver.find_element_by_class_name("cart_button").click()
        self.wait_for_page_by_id("checkout_complete_container")
        self.url_assert("checkout-complete.html")

        header_text = self.driver.find_element_by_class_name("complete-header").text
        expected = u"THANK YOU FOR YOUR ORDER"
        assert header_text == expected, "Expected: {}\nGot: {}".format(expected, header_text)


    def test_all_the_way_through_every_item(self):
        """Log in, add every item to the basket, proceed to checkout, then checkout"""
        self.login_page_setup()

        self.complete_login_page("standard_user")
        self.wait_for_page_by_id("searchbox_container")
        self.url_assert("inventory.html")
        # Logged in at this point - Inventory page

        # Add every item to the cart
        item_list = self.driver.find_elements_by_class_name("inventory_item")
        expected_cart = [item.find_element_by_class_name("inventory_item_name").text for item in item_list].sort()
        button_list = [button.find_element_by_xpath(".//div[@class='pricebar']/button") for button in item_list]

        for count, button in enumerate(button_list):
            button.click()
            # Want to be sure it added the item
            assert button.text == u"REMOVE",\
                   "Expected button to say 'REMOVE', actually said {}".format(button.text)
            
            # Test the cart counter is going up as we add more items
            item_count = self.driver.find_element_by_class_name("fa-layers-counter").text
            assert item_count == u"{}".format(count + 1),\
                   "Expected item count to be {}, was actually {}".format(count + 1, item_count)

        # Go to next page - Cart
        self.driver.find_element_by_class_name("shopping_cart_link").click()
        self.wait_for_page_by_class("cart_list")
        self.url_assert("cart.html")
        try:
            # Check there are items in the cart
            self.driver.find_element_by_class_name("cart_item")
        except NoSuchElementException:
            self.fail("There were no items in the cart, expected {}".format(len(item_list)))

        # Check that every item we added is in the cart
        cart = [item.text for item in self.driver.find_elements_by_class_name("inventory_item_name")].sort()
        assert cart == expected_cart,\
               "Expected cart to be: {} but it was {}".format(expected_cart, cart)

        # Go to next page - Checkout step one
        self.driver.find_element_by_class_name("checkout_button").click()
        self.wait_for_page_by_id("checkout_info_container")
        self.url_assert("checkout-step-one.html")
        self.complete_checkout_step_one()

        # Go to next page
        self.wait_for_page_by_id("checkout_summary_container")
        self.url_assert("checkout-step-two.html")
        checkout_cart_list = [item.text for item in self.driver.find_elements_by_class_name("inventory_item_name")].sort()
        assert expected_cart == checkout_cart_list,\
               "Expected cart to be {} but got {}".format(expected_cart, checkout_cart_list)


        # Go to next page
        self.driver.find_element_by_class_name("cart_button").click()
        self.wait_for_page_by_id("checkout_complete_container")
        self.url_assert("checkout-complete.html")

        header_text = self.driver.find_element_by_class_name("complete-header").text
        expected = u"THANK YOU FOR YOUR ORDER"
        assert header_text == expected, "Expected: {}\nGot: {}".format(expected, header_text)


    def test_all_the_way_through_random_items(self):
        """Log in, add three random items to the basket, proceed to checkout, then checkout"""
        self.login_page_setup()

        self.complete_login_page("standard_user")
        self.wait_for_page_by_id("searchbox_container")
        self.url_assert("inventory.html")
        # Logged in at this point - Inventory page

        # Add every item to the cart
        item_list = sample(self.driver.find_elements_by_class_name("inventory_item"), 3)
        expected_cart = [item.find_element_by_class_name("inventory_item_name").text for item in item_list].sort()
        button_list = [button.find_element_by_xpath(".//div[@class='pricebar']/button") for button in item_list]

        for count, button in enumerate(button_list):
            button.click()
            # Want to be sure it added the item
            assert button.text == u"REMOVE",\
                   "Expected button to say 'REMOVE', actually said {}".format(button.text)
            
            item_count = self.driver.find_element_by_class_name("fa-layers-counter").text
            assert item_count == u"{}".format(count + 1),\
                   "Expected item count to be {}, was actually {}".format(count + 1, item_count)

        # Go to next page - Cart
        self.driver.find_element_by_class_name("shopping_cart_link").click()
        self.wait_for_page_by_class("cart_list")
        self.url_assert("cart.html")
        try:
            # Check the item we added is in the cart
            self.driver.find_element_by_class_name("cart_item")
        except NoSuchElementException:
            self.fail("There were no items in the cart, expected one")

        # Go to next page - Checkout step one
        self.driver.find_element_by_class_name("checkout_button").click()
        self.wait_for_page_by_id("checkout_info_container")
        self.url_assert("checkout-step-one.html")
        self.complete_checkout_step_one()
        self.wait_for_page_by_id("checkout_summary_container")
        self.url_assert("checkout-step-two.html")
        checkout_cart_list = [item.text for item in self.driver.find_elements_by_class_name("inventory_item_name")].sort()
        assert expected_cart == checkout_cart_list,\
               "Expected cart to be {} but got {}".format(expected_cart, checkout_cart_list)

        # Go to next page
        self.driver.find_element_by_class_name("cart_button").click()
        self.wait_for_page_by_id("checkout_complete_container")
        self.url_assert("checkout-complete.html")


        header_text = self.driver.find_element_by_class_name("complete-header").text
        expected = u"THANK YOU FOR YOUR ORDER"
        assert header_text == expected, "Expected: {}\nGot: {}".format(expected, header_text)
