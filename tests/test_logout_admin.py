import pytest
from pages.logout_admin_pages import LogoutAdminPages
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import allure


@pytest.fixture
def logout_admin_page(browser, base_url):
    logout_page = LogoutAdminPages(browser, base_url)
    logout_page.open()
    return logout_page


@allure.feature("Выход из системы администратора")
@allure.story("Тестирование процесса выхода из системы администратора")
def test_logout_admin(logout_admin_page):
    USERNAME = "user"
    PASSWORD = "bitnami"

    with allure.step(f"Ввод имени пользователя: {USERNAME}"):
        logout_admin_page.enter_username(USERNAME)

    with allure.step(f"Ввод пароля: {PASSWORD}"):
        logout_admin_page.enter_password(PASSWORD)

    with allure.step("Нажатие кнопки входа в систему"):
        logout_admin_page.click_login_button()

    with allure.step(f"Проверка заголовка страницы после входа в систему"):
        expected_title_after_login = "Dashboard"
        WebDriverWait(logout_admin_page.browser, 5).until(
            EC.title_contains(expected_title_after_login)
        )
    assert (
        expected_title_after_login in logout_admin_page.get_title()
    ), f"Ожидаемый заголовок '{expected_title_after_login}' не соответствует фактическому заголовку '{logout_admin_page.get_title()}'"

    with allure.step("Выход из системы"):
        logout_admin_page.logout()
