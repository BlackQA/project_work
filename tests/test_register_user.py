from pages.register_user_pages import RegisterNewUser
import pytest
import allure
from faker import Faker

fake = Faker()


@pytest.fixture(scope="function")
def reset_browser(browser, base_url):
    browser.delete_all_cookies()
    browser.get(base_url + "/logout")
    yield


@pytest.mark.parametrize(
    "first_name, last_name, email, password, expected_message",
    [
        (
            "John",
            "Connor",
            fake.email(),
            "12345",
            "Your Account Has Been Created!",
        ),
        (
            "Alexander-the-veeery-long-name-33",
            "McDonald",
            fake.email(),
            "12345",
            "Register Account",
        ),
        (
            fake.random_int(min=10, max=1000),
            "Smith",
            fake.email(),
            "12345",
            "Your Account Has Been Created!",
        ),
        (
            "@@@!!$%^&",
            "Jones",
            fake.email(),
            "12345",
            "Your Account Has Been Created!",
        ),
    ],
    ids=[
        "standard",
        "long_name",
        "numbers_in_name",
        "special_chars_in_name",
    ],
)
@allure.feature("Регистрация нового пользователя")
@allure.story("Тестирование процесса регистрации нового пользователя")
def test_register_new_user(
    reset_browser,
    browser,
    base_url,
    first_name,
    last_name,
    email,
    password,
    expected_message,
):

    with allure.step("Открытие страницы регистрации"):
        register_user = RegisterNewUser(browser, base_url)
        register_user.open()

    with allure.step("Ввод имени"):
        register_user.enter_first_name(first_name)

    with allure.step("Ввод фамилии"):
        register_user.enter_last_name(last_name)

    with allure.step("Ввод email"):
        register_user.enter_email(email)

    with allure.step("Ввод пароля"):
        register_user.enter_password(password)

    with allure.step("Принятие политики конфиденциальности"):
        register_user.click_checkbox_button()

    with allure.step("Нажатие кнопки продолжения"):
        register_user.click_continue_button()

    with allure.step("Проверка сообщения об успешной регистрации"):
        register_user.get_message(expected_text=expected_message)
