from pages.admin_product_new_pages import AdminProductNew
import pytest
import allure
from faker import Faker

faker = Faker()


@pytest.fixture(scope="function")
def reset_browser(browser, base_url):
    browser.delete_all_cookies()
    browser.get(base_url + "/logout")
    yield


@pytest.mark.parametrize(
    "username, password, product_name, meta_tag, model, seo_keyword, expected_message",
    [
        (
            "user",
            "bitnami",
            "Новый Товар 1",
            "Мета-тег для нового товара 1",
            "MODEL123",
            faker.lexify(text="seo_??????"),
            "Success: You have modified products!",
        ),
        (
            "user",
            "bitnami",
            " ",
            "Мета-тег для нового товара 2",
            "MODEL124",
            faker.lexify(text="seo_??????"),
            "Warning: Please check the form carefully for errors!",
        ),
        (
            "user",
            "bitnami",
            "Новый Товар 3",
            "Мета-тег для нового товара 3",
            "MODEL125",
            "@#$",
            "Warning: Please check the form carefully for errors!",
        ),
        (
            "user",
            "bitnami",
            "A",
            "B",
            "C",
            faker.lexify(text="?"),
            "Success: You have modified products!",
        ),
        (
            "user",
            "bitnami",
            "Новый Товар 13",
            "Meta Tag",
            "MODEL125",
            "русский_язык",
            "Warning: Please check the form carefully for errors!",
        ),
    ],
    ids=["standard", "name_empty", "invalid_seo", "minimal_values", "rus_seo"],
)
@allure.feature("Создание нового продукта")
@allure.story("Тестирование процесса создания нового продукта")
def test_add_new_product(
    browser,
    base_url,
    username,
    password,
    product_name,
    meta_tag,
    model,
    seo_keyword,
    expected_message,
):
    with allure.step("Создание экземпляра AdminProductNew"):
        admin_product_new = AdminProductNew(browser, base_url)
    with allure.step("Открытие страницы администрирования"):
        admin_product_new.open()
    with allure.step("Вход в систему"):
        admin_product_new.enter_username(username)
        admin_product_new.enter_password(password)
        admin_product_new.click_login_button()
    with allure.step("Навигация к разделу каталога и продуктам"):
        admin_product_new.click_catalog_button()
        admin_product_new.click_product_button()
    with allure.step("Добавление нового продукта"):
        admin_product_new.add_product(product_name, meta_tag, model, seo_keyword)
    with allure.step("Проверка сообщения об успешном добавлении продукта"):
        admin_product_new.get_success_message(expected_text=expected_message)
