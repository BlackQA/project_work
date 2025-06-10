import logging
import pytest
import allure
import json
import os
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.chromium.service import ChromiumService
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FFOptions


logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("../../pytest.log"), logging.StreamHandler()],
)


def pytest_addoption(parser):
    parser.addoption(
        "--browser",
        action="store",
        default="chrome",
        help="Browser to run tests: chrome, firefox, yandex",
    )
    parser.addoption(
        "--base_url",
        action="store",
        default="http://192.168.0.119:8081/",
        help="Base URL OpenCart",
    )
    parser.addoption(
        "--headless",
        action="store_true",
        default=True,
        help="Run tests in headless mode",
    )


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
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


@pytest.fixture(scope="session")
def browser(request):
    browser_name = request.config.getoption("--browser").lower()
    base_url = request.config.getoption("--base_url")
    headless = request.config.getoption("--headless")

    logger.info(f"Starting {browser_name} browser, headless={headless}")

    driver = None
    try:
        if browser_name in ["chrome", "ch"]:
            options = ChromeOptions()
            if headless:
                options.add_argument("--headless=new")
                options.add_argument("--window-size=1920,1080")
                options.add_argument("--disable-gpu")
                options.add_argument("--no-sandbox")
                options.add_argument("--disable-dev-shm-usage")
                options.add_argument("--remote-debugging-port=9222")
                options.add_argument("--start-maximized")
                options.add_argument("--disable-infobars")
                options.add_argument("--disable-extensions")
                options.add_argument("--disable-notifications")
                options.add_argument("--lang=en-US")
            driver = webdriver.Chrome(options=options)

        elif browser_name in ["firefox", "ff"]:
            options = FFOptions()
            if headless:
                options.add_argument("--headless")
            driver = webdriver.Firefox(options=options)

        elif browser_name in ["yandex", "ya"]:
            options = ChromeOptions()
            if headless:
                options.add_argument("--headless=new")
            service = ChromiumService(
                executable_path="/Users/userqa/Documents/drivers/yandexdriver"
            )
            driver = webdriver.Chrome(service=service, options=options)

        else:
            raise ValueError(f"Unsupported browser: {browser_name}")

        driver.implicitly_wait(10)

        allure.attach(
            name="browser_capabilities",
            body=json.dumps(driver.capabilities, indent=4, ensure_ascii=False),
            attachment_type=allure.attachment_type.JSON,
        )

        driver.test_name = request.node.name
        driver.start_time = datetime.now()

        driver.set_window_size(1920, 1080)
        driver.get(base_url)
        WebDriverWait(driver, 20).until(
            lambda d: d.execute_script("return document.readyState") == "complete"
        )
        logger.info(f"Opened URL: {base_url}")

        request.session.driver = driver

        yield driver

    except WebDriverException as e:
        logger.error(f"WebDriver error during initialization: {str(e)}")
        pytest.fail(f"WebDriver error: {str(e)}")

    except Exception as e:
        logger.error(f"Browser initialization failed: {str(e)}")
        pytest.fail(f"Browser initialization failed: {str(e)}")

    finally:
        if (
            driver
            and hasattr(request.node, "rep_call")
            and request.node.rep_call.failed
        ):
            try:
                allure.attach(
                    driver.get_screenshot_as_png(),
                    name="final_screenshot",
                    attachment_type=allure.attachment_type.PNG,
                )
            except Exception as e:
                logger.error(f"Failed to take final screenshot: {str(e)}")

        if driver:
            driver.quit()
            logger.info("Browser closed")


@pytest.fixture(scope="session")
def base_url(request):
    return request.config.getoption("--base_url")


@pytest.fixture(autouse=True)
def log_test_info(request):
    logger.info(f"\n=== Starting test: {request.node.name} ===\n")
    yield
    logger.info(f"\n=== Finished test: {request.node.name} ===\n")
