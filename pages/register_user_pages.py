from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import allure
import logging
import os


class RegisterNewUser:
    FirstName_input = (By.XPATH, "//*[@id='input-firstname']")
    LastName_input = (By.XPATH, "//*[@id='input-lastname']")
    Email_input = (By.XPATH, "//*[@id='input-email']")
    Password_input = (By.XPATH, "//*[@id='input-password']")
    Policy_checkbox = (By.XPATH, "//*[@id='form-register']/div/div/input")
    Continue_button = (By.XPATH, "//*[@id='form-register']/div/button")
    Text_created = (By.XPATH, "//*[@id='content']/h1")

    def __init__(self, browser, base_url, to_file=True):
        self.browser = browser
        self.base_url = base_url
        self.wait = WebDriverWait(browser, 10)
        self.logger = logging.getLogger(self.__class__.__name__)
        os.makedirs("logs", exist_ok=True)
        if to_file:
            self.logger.addHandler(
                logging.FileHandler(f"logs/{self.browser.test_name}.log")
            )

    @allure.step("Открытие страницы регистрации")
    def open(self):
        catalog_url = self.base_url + "/en-gb?route=account/register"
        self.logger.info(f"Opening URL: {catalog_url}")
        self.browser.get(catalog_url)

    @allure.step("Ввод имени: {first_name}")
    def enter_first_name(self, first_name):
        self.logger.info(f"Entering first name: {first_name}")
        username_input = self.wait.until(
            EC.visibility_of_element_located(self.FirstName_input)
        )
        username_input.clear()
        username_input.send_keys(first_name)

    @allure.step("Ввод фамилии: {last_name}")
    def enter_last_name(self, last_name):
        self.logger.info(f"Entering last name: {last_name}")
        lastname_input = self.wait.until(
            EC.visibility_of_element_located(self.LastName_input)
        )
        lastname_input.clear()
        lastname_input.send_keys(last_name)

    @allure.step("Ввод email: {email}")
    def enter_email(self, email):
        self.logger.info(f"Entering email: {email}")
        email_input = self.wait.until(
            EC.visibility_of_element_located(self.Email_input)
        )
        email_input.clear()
        email_input.send_keys(email)

    @allure.step("Ввод пароля: {password}")
    def enter_password(self, password):
        self.logger.info(f"Entering password: {password}")
        password_input = self.wait.until(
            EC.visibility_of_element_located(self.Password_input)
        )
        password_input.clear()
        password_input.send_keys(password)

    @allure.step("Принятие политики конфиденциальности")
    def click_checkbox_button(self):
        self.logger.info("Clicking on the policy checkbox")
        button = self.wait.until(EC.element_to_be_clickable(self.Policy_checkbox))
        self.browser.execute_script("arguments[0].scrollIntoView(true);", button)
        time.sleep(0.5)
        button.click()

    @allure.step("Нажатие кнопки продолжения")
    def click_continue_button(self):
        self.logger.info("Clicking on the continue button")
        button = self.wait.until(EC.element_to_be_clickable(self.Continue_button))
        button.click()
        time.sleep(0.5)

    @allure.step("Проверка сообщения об успешной регистрации: {expected_text}")
    def get_message(self, expected_text="Your Account Has Been Created!"):
        self.logger.info(f"Checking for message: {expected_text}")
        message = self.wait.until(
            EC.visibility_of_element_located(self.Text_created),
            "Текс о создании нового пользователя не появился",
        )
        actual_text = message.text
        assert (
            expected_text in actual_text
        ), f"Текст сообщения не соответствует ожидаемому. Ожидалось: '{expected_text}', получили: '{actual_text}'"

        self.logger.info("Message verified successfully")
