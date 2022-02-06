import pytest
import os
import datetime
import random
import logging
from selenium import webdriver


def pytest_addoption(parser):
    parser.addoption("--browser", action="store", default="chrome")
    parser.addoption("--url", action="store", default="local")  # 127.0.0.1
    parser.addoption("--drivers", action="store", default=os.path.expanduser("C:/drivers1"))
    parser.addoption("--log_level", action="store", default="DEBUG")
    parser.addoption("--bversion", action="store", default="98.0")
    parser.addoption("--vnc", action="store_true", default=False)
    parser.addoption("--logs", action="store_true", default=False)
    parser.addoption("--videos", action="store_true", default=True)


@pytest.fixture
def browser(request):
    browser = request.config.getoption("--browser")
    executor = request.config.getoption("--url")
    drivers = request.config.getoption("--drivers")
    log_level = request.config.getoption("--log_level")
    version = request.config.getoption("--bversion")
    vnc = request.config.getoption("--vnc")
    logs = request.config.getoption("--logs")
    videos = request.config.getoption("--videos")

    if executor == "local":
        if browser == "chrome":
            wd = webdriver.Chrome(executable_path=drivers + "/chromedriver")
        elif browser == "firefox":
            wd = webdriver.Firefox(executable_path=drivers + "/geckodriver")
        elif browser == "opera":
            wd = webdriver.Opera(executable_path=drivers + "/operadriver")
        wd.maximize_window()

    else:
        executor_url = f"http://{executor}:4444/wd/hub"

        caps = {
            "browserName": browser,
            "browserVersion": version,
            "screenResolution": "1280x1024",
            "name": "Opencart tests",
            "selenoid:options": {
                "sessionTimeout": "60s",
                "enableVNC": vnc,
                "enableVideo": videos,
                "enableLog": logs
            }
        }

        wd = webdriver.Remote(
            command_executor=executor_url,
            desired_capabilities=caps
        )

        wd.maximize_window()

    logger = logging.getLogger('driver')

    test_name = request.node.name

    logger.addHandler(logging.FileHandler(f"logs/{test_name}.log"))
    logger.setLevel(level=log_level)
    logger.info("===> Test {} started at {}".format(test_name, datetime.datetime.now()))
    wd.test_name = test_name
    wd.log_level = log_level
    logger.info("Browser:{}".format(browser, wd.desired_capabilities))

    wd.url = "http://demo.opencart.com"
    wd.get(wd.url)

    def fin():
        with open('allure-results/environment.properties', 'w') as f:
            f.write(f'Browser={browser}\n')
            f.write(f'Browser.Version={version}\n')
            f.write(f'Executor={executor}')
        wd.quit()
        logger.info("===> Test {} finished at {}".format(test_name, datetime.datetime.now()))

    request.addfinalizer(fin)
    return wd


@pytest.fixture
def create_user():
    letters = ["a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l", "m", "n",
               "o", "p", "q", "r", "s", "t", "u", "v", "w", "x", "y", "z", ]
    numbers = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9", ]
    email = ''
    phone = '+7'
    for i in range(10):
        email += random.sample(letters, 1)[0]
        phone += random.sample(numbers, 1)[0]
    email += '@gmail.com'
    return (email, phone)
