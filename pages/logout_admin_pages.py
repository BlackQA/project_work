from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import logging
import allure
import os


class LogoutAdminPages:
    Username_input = (By.XPATH, "//*[@id='input-username']")
    Password_input = (By.XPATH, "//*[@id='input-password']")
    Button_login = (By.XPATH, "//*[@id='form-login']/div[3]/button")
    Button_logout = (By.XPATH, "//*[@id='nav-logout']/a")

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

    @allure.step("Открытие страницы администрирования")
    def open(self):
        catalog_url = self.base_url + "/administration"
        self.logger.info(f"Opening admin page: {catalog_url}")
        self.browser.get(catalog_url)

    @allure.step("Ввод имени пользователя: {username}")
    def enter_username(self, username):
        self.logger.info(f"Entering username: {username}")
        username_input = self.wait.until(
            EC.visibility_of_element_located(self.Username_input)
        )
        username_input.clear()
        username_input.send_keys(username)

    @allure.step("Ввод пароля: {password}")
    def enter_password(self, password):
        self.logger.info(f"Entering password: {password}")
        password_input = self.wait.until(
            EC.visibility_of_element_located(self.Password_input)
        )
        password_input.clear()
        password_input.send_keys(password)

    @allure.step("Нажатие кнопки входа в систему")
    def click_login_button(self):
        self.logger.info("Clicking on login button")
        button = self.wait.until(EC.element_to_be_clickable(self.Button_login))
        button.click()

    @allure.step("Получение кнопки выхода из системы")
    def get_logout_button(self):
        self.logger.info("Getting logout button")
        return self.wait.until(EC.visibility_of_element_located(self.Button_logout))

    @allure.step("Выход из системы")
    def logout(self):
        self.logger.info("Logging out")
        logout_button = self.get_logout_button()
        logout_button.click()

    @allure.step("Получение кнопки входа в систему после выхода")
    def get_login_button_after_logout(self):
        self.logger.info("Getting login button after logout")
        return self.wait.until(EC.visibility_of_element_located(self.Button_login))

    @allure.step("Получение заголовка страницы")
    def get_title(self):
        self.logger.info("Getting page title")
        return self.browser.title
