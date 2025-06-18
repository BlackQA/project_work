import logging
import pytest
import allure
import json
import os
import platform
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.firefox.options import Options as FFOptions
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager

# Настройка логирования
logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(os.path.join(os.getcwd(), "pytest.log")),
        logging.StreamHandler()
    ],
)


def pytest_addoption(parser):
    """Регистрация кастомных параметров pytest"""
    parser.addoption(
        "--browser",
        action="store",
        default="chrome",
        help="Browser to run tests: chrome, firefox, yandex",
        choices=["chrome", "firefox", "yandex"]
    )
    parser.addoption(
        "--base_url",
        action="store",
        default="http://192.168.0.119:8081/",
        help="Base application URL"
    )
    parser.addoption(
        "--headless",
        action="store_true",
        default=True,
        help="Run tests in headless mode"
    )


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """Создание отчетов и скриншотов для упавших тестов"""
    outcome = yield
    rep = outcome.get_result()

    if rep.when == "call" and rep.failed:
        driver = getattr(item.session, "driver", None)
        if driver:
            try:
                screenshot_dir = os.path.join("allure-results", "screenshots")
                os.makedirs(screenshot_dir, exist_ok=True)
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                screenshot_path = os.path.join(
                    screenshot_dir, f"{item.name}_{timestamp}.png"
                )

                driver.save_screenshot(screenshot_path)
                logger.error(f"Test failed, screenshot saved to: {screenshot_path}")

                allure.attach(
                    driver.get_screenshot_as_png(),
                    name=f"screenshot_{item.name}",
                    attachment_type=allure.attachment_type.PNG,
                )
            except Exception as e:
                logger.error(f"Failed to take screenshot: {str(e)}")


@pytest.fixture(scope="function")
def browser(request):
    """Фикстура для инициализации браузера с поддержкой test_name"""
    browser_name = request.config.getoption("--browser").lower()
    base_url = request.config.getoption("--base_url")
    headless = request.config.getoption("--headless")

    # Определяем окружение
    is_jenkins = "JENKINS_HOME" in os.environ
    is_docker = os.path.exists("/.dockerenv")
    is_mac_arm = platform.system() == 'Darwin' and platform.machine() == 'arm64'

    logger.info(f"Starting {browser_name} browser (headless={headless})")

    driver = None
    try:
        if browser_name in ["chrome", "ch"]:
            options = ChromeOptions()

            # Общие настройки
            options.add_argument("--window-size=1920,1080")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")

            # Настройки для Mac M1
            if is_mac_arm:
                options.binary_location = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

            # Headless режим
            if headless:
                options.add_argument("--headless=new")
                options.add_argument("--disable-gpu")

            # Настройки для CI
            if is_jenkins or is_docker:
                options.add_argument("--remote-debugging-port=9222")
                options.add_argument("--disable-extensions")
                options.add_argument("--disable-logging")
                options.add_argument("--log-level=3")

            # Инициализация драйвера
            service = ChromeService(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=options)

        elif browser_name in ["firefox", "ff"]:
            options = FFOptions()

            if headless:
                options.add_argument("--headless")

            service = FirefoxService(GeckoDriverManager().install())
            driver = webdriver.Firefox(service=service, options=options)

        elif browser_name in ["yandex", "ya"]:
            options = ChromeOptions()

            if headless:
                options.add_argument("--headless=new")

            # Для Yandex используем ChromeDriver с указанием пути к бинарнику Yandex
            options.binary_location = "/Applications/Yandex.app/Contents/MacOS/Yandex"
            service = ChromeService(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=options)

        # Добавляем атрибуты для совместимости с существующими тестами
        driver.test_name = request.node.name
        driver.start_time = datetime.now()

        # Сохраняем драйвер в сессии
        request.session.driver = driver

        # Логирование возможностей браузера
        allure.attach(
            name="browser_capabilities",
            body=json.dumps(driver.capabilities, indent=4, ensure_ascii=False),
            attachment_type=allure.attachment_type.JSON,
        )

        # Открытие базового URL
        driver.get(base_url)
        WebDriverWait(driver, 20).until(
            lambda d: d.execute_script("return document.readyState") == "complete"
        )
        logger.info(f"Successfully opened URL: {base_url}")

        yield driver

    except WebDriverException as e:
        logger.error(f"WebDriver error: {str(e)}")
        pytest.fail(f"WebDriver error: {str(e)}")

    finally:
        if driver:
            driver.quit()
            logger.info("Browser closed")


@pytest.fixture(scope="session")
def base_url(request):
    """Фикстура для базового URL"""
    return request.config.getoption("--base_url")


@pytest.fixture(autouse=True)
def log_test_info(request):
    """Фикстура для логирования информации о тестах"""
    logger.info(f"\n=== Starting test: {request.node.name} ===\n")
    yield
    logger.info(f"\n=== Finished test: {request.node.name} ===\n")


def pytest_configure(config):
    """Конфигурация pytest при запуске"""
    os.makedirs("allure-results/screenshots", exist_ok=True)
    os.makedirs("test-results", exist_ok=True)
    logger.info("Pytest configuration completed")