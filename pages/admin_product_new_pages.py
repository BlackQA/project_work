from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import allure
import logging
import os
import time


class AdminProductNew:
    Username_input = (By.XPATH, "//*[@id='input-username']")
    Password_input = (By.XPATH, "//*[@id='input-password']")
    Button_login = (By.XPATH, "//*[@id='form-login']/div[3]/button")

    Catalog_button = (By.XPATH, "//*[@id='menu-catalog']/a")
    Product_button = (By.XPATH, "//*[@id='collapse-1']/li[2]/a")

    Add_new = (By.XPATH, "//*[@id='content']/div[1]/div/div/a")
    Name_input = (By.XPATH, "//*[@id='input-name-1']")
    Meta_input = (By.XPATH, "//*[@id='input-meta-title-1']")
    Data_button = (By.XPATH, "//*[@id='form-product']/ul/li[2]/a")
    Model_input = (By.XPATH, "//*[@id='input-model']")
    Seo_button = (By.XPATH, "//*[@id='form-product']/ul/li[11]/a")
    Seo_input = (By.XPATH, "//*[@id='input-keyword-0-1']")
    Save_button = (By.XPATH, "//*[@id='content']/div[1]/div/div/button")
    Alert = (By.XPATH, "//*[@id='alert']")

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

    @allure.step("Открытие страницы")
    def open(self):
        catalog_url = self.base_url + "/administration"
        self.logger.info(f"Opening URL: {catalog_url}")
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

    def _click(self, locator):
        button = self.wait.until(
            EC.element_to_be_clickable(locator),
            f"Элемент с локатором {locator} не кликабелен",
        )
        button.click()

    @allure.step("Нажатие кнопки входа в систему")
    def click_login_button(self):
        self._click(self.Button_login)

    @allure.step("Нажатие кнопки каталога")
    def click_catalog_button(self):
        self._click(self.Catalog_button)

    @allure.step("Нажатие кнопки продукта")
    def click_product_button(self):
        self._click(self.Product_button)

    @allure.step("Нажатие кнопки добавления нового продукта")
    def click_add_new_button(self):
        self._click(self.Add_new)

    @allure.step("Ввод названия продукта: {product_input}")
    def enter_product_name(self, product_input):
        self.logger.info(f"Entering product name: {product_input}")
        product_name = self.wait.until(
            EC.visibility_of_element_located(self.Name_input)
        )
        product_name.clear()
        product_name.send_keys(product_input)

    @allure.step("Ввод мета-тега: {meta}")
    def enter_meta_tag(self, meta):
        self.logger.info(f"Entering meta tag: {meta}")
        meta_tag = self.wait.until(EC.visibility_of_element_located(self.Meta_input))
        meta_tag.clear()
        meta_tag.send_keys(meta)

    @allure.step("Нажатие кнопки Data")
    def click_data_button(self):
        self._click(self.Data_button)

    @allure.step("Ввод модели: {model}")
    def enter_model_input(self, model):
        self.logger.info(f"Entering model: {model}")
        model_input = self.wait.until(
            EC.visibility_of_element_located(self.Model_input)
        )
        model_input.clear()
        model_input.send_keys(model)

    @allure.step("Нажатие кнопки SEO")
    def click_seo_button(self):
        self._click(self.Seo_button)

    @allure.step("Ввод SEO: {seo}")
    def enter_seo_input(self, seo):
        self.logger.info(f"Entering SEO keyword: {seo}")
        seo_input = self.wait.until(EC.visibility_of_element_located(self.Seo_input))
        seo_input.clear()
        seo_input.send_keys(seo)

    @allure.step("Нажатие кнопки сохранения")
    def click_save_button(self):
        self._click(self.Save_button)
        time.sleep(0.5)

    @allure.step("Получение сообщения об успешном добавлении продукта: {expected_text}")
    def get_success_message(self, expected_text="Success: You have modified products!"):
        self.logger.info(f"Checking for message: {expected_text}")
        success_message = self.wait.until(
            EC.visibility_of_element_located(self.Alert),
            "Сообщение об успешном добавлении товара не появилось",
        )
        actual_text = success_message.text
        assert (
            expected_text in actual_text
        ), f"Текст сообщения не соответствует ожидаемому. Ожидалось: '{expected_text}', получили: '{actual_text}'"

        self.logger.info("Message verified successfully")

    @allure.step(
        "Добавление нового продукта: {product_name}, {meta_tag}, {model}, {seo_keyword}"
    )
    def add_product(self, product_name, meta_tag, model, seo_keyword):
        self.click_add_new_button()
        self.enter_product_name(product_name)
        self.enter_meta_tag(meta_tag)
        self.click_data_button()
        self.enter_model_input(model)
        self.click_seo_button()
        self.enter_seo_input(seo_keyword)
        self.click_save_button()
