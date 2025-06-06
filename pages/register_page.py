from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import logging
import allure
import os


class RegisterPage:
    Firstname_input = (By.XPATH, "//*[@id='input-firstname']")
    Lastname_input = (By.XPATH, "//*[@id='input-lastname']")
    Email_input = (By.XPATH, "//*[@id='input-email']")
    Password_input = (By.XPATH, "//*[@id='input-password']")
    Button_register = (By.XPATH, "//*[@id='form-register']/div/button")

    def __init__(self, browser, base_url, to_file=True):
        self.browser = browser
        self.base_url = base_url
        self.wait = WebDriverWait(browser, 5)
        self.logger = logging.getLogger(self.__class__.__name__)
        os.makedirs("logs", exist_ok=True)
        if to_file:
            self.logger.addHandler(
                logging.FileHandler(f"logs/{self.browser.test_name}.log")
            )

    @allure.step("Открытие страницы регистрации")
    def open(self):
        catalog_url = self.base_url + "/en-gb?route=account/register"
        self.logger.info(f"Opening register page:: {catalog_url}")
        self.browser.get(catalog_url)

    @allure.step("Получение поля First Name")
    def get_firstname_input(self):
        self.logger.info(f"Getting Firs Name")
        return self.wait.until(EC.visibility_of_element_located(self.Firstname_input))

    @allure.step("Получение поля Last Name")
    def get_lastname_input(self):
        self.logger.info(f"Getting Last Name")
        return self.wait.until(EC.visibility_of_element_located(self.Lastname_input))

    @allure.step("Получение поля Email")
    def get_email_input(self):
        self.logger.info(f"Getting Email")
        return self.wait.until(EC.visibility_of_element_located(self.Email_input))

    @allure.step("Получение поля Password")
    def get_password_input(self):
        self.logger.info(f"Getting Password")
        return self.wait.until(EC.visibility_of_element_located(self.Password_input))

    @allure.step("Получение кнопки Register")
    def get_button_register(self):
        self.logger.info(f"Getting button Register")
        return self.wait.until(EC.element_to_be_clickable(self.Button_register))
