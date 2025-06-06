from pages.register_page import RegisterPage
import allure


@allure.feature("Проверка элементов регистрации")
@allure.story("Тестирование страницы регистрации")
def test_register_page(browser, base_url):

    with allure.step("Открытие страницы регистрации"):
        register_page = RegisterPage(browser, base_url)
        register_page.open()

    with allure.step("Проверка поля First Name"):
        assert (
            register_page.get_firstname_input().is_displayed()
        ), "Поле ввода имени не отображается"

    with allure.step("Проверка поля Last Name"):
        assert (
            register_page.get_lastname_input().is_displayed()
        ), "Поле ввода фамилии не отображается"

    with allure.step("Проверка поля email"):
        assert (
            register_page.get_email_input().is_displayed()
        ), "Поле ввода email не отображается"

    with allure.step("Проверка поля Password"):
        assert (
            register_page.get_password_input().is_displayed()
        ), "Поле ввода пароля не отображается"

    with allure.step("Проверка кнопки Register"):
        assert (
            register_page.get_button_register().is_displayed()
        ), "Кнопка 'Continue' не отображается"
