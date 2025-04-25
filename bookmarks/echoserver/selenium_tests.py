from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import pytest
import time
from selenium.common.exceptions import TimeoutException


@pytest.fixture(scope="module")
def driver():
    # Настройка драйвера
    # options.add_argument("--headless=new")  # закомментируйте эту строку
    options = webdriver.ChromeOptions()
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--force-device-scale-factor=1")
    options.add_experimental_option("prefs", {
        "intl.accept_languages": "ru-RU,ru",
        "profile.managed_default_content_settings.javascript": 1
    })
    options.add_argument("--enable-javascript")
    options.add_experimental_option("excludeSwitches", ["disable-javascript"])
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-infobars")
    options.add_argument("--disable-notifications")

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    driver.implicitly_wait(25)
    driver.set_window_size(1920, 1080)

    yield driver
    driver.quit()


def test_user_registration_and_login(driver):
    try:
        # Генерация уникальных тестовых данных
        timestamp = str(int(time.time()))
        username = f"testuser_{timestamp}"
        email = f"test_{timestamp}@example.com"
        password = "TestPass123!"

        # Шаг 1: Регистрация нового пользователя
        driver.get("http://localhost:8000/register/")  # Явное указание слеша
        
        # Ожидание загрузки формы
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.NAME, "username"))
        )

        # Заполнение формы
        driver.find_element(By.NAME, "username").send_keys(username)
        driver.find_element(By.NAME, "email").send_keys(email)
        driver.find_element(By.NAME, "password").send_keys(password)
        driver.find_element(By.NAME, "confirm_password").send_keys(password)
        
        # Скриншот перед отправкой
        driver.save_screenshot("before_registration.png")
        
        # Отправка формы
        submit_button = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
        submit_button.click()

        # Шаг 2: Проверка успешной регистрации
        try:
            WebDriverWait(driver, 15).until(
                EC.any_of(
                    EC.url_contains("/login"),
                    EC.presence_of_element_located((By.CLASS_NAME, "alert-success"))
                )
            )
        except TimeoutException:
            driver.save_screenshot("registration_timeout.png")
            # Проверка ошибок валидации
            errors = driver.find_elements(By.CSS_SELECTOR, ".error, .alert-danger")
            if errors:
                error_text = "\n".join([e.text for e in errors if e.text])
                raise AssertionError(f"Ошибки регистрации:\n{error_text}")
            raise

        # Шаг 3: Авторизация
        driver.get("http://localhost:8000/login/")
        
        # Явная проверка языка интерфейса
        WebDriverWait(driver, 20).until(
            lambda d: "Войти" in d.page_source and "Логин" not in d.page_source
        )
        
        # Улучшенный локатор для кнопки
        login_button = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable(
                (By.XPATH, "//button[normalize-space()='Войти']")
            )
        )
        login_button.click()

        # После клика на кнопку входа
        current_url = driver.current_url
        print(f"Current URL after login: {current_url}")
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "user-panel"))
        )

        # Шаг 4: Проверка успешного входа
        WebDriverWait(driver, 15).until(
            EC.text_to_be_present_in_element(
                (By.XPATH, "//div[@class='user-panel']/p/strong"),
                username
            )
        )

        # Проверка сообщений об ошибках
        error_messages = driver.find_elements(By.CLASS_NAME, "alert-danger")
        if error_messages:
            errors = "\n".join([m.text for m in error_messages if m.text])
            raise AssertionError(f"Ошибки авторизации:\n{errors}")

        # Дополнительная проверка URL
        WebDriverWait(driver, 10).until(
            EC.url_contains("book_list")
        )

    except Exception as e:
        with open("error_page.html", "w", encoding="utf-8") as f:
            f.write(driver.page_source)
        driver.save_screenshot("registration_test_error.png")
        raise e


def test_cart_functionality(driver):
    try:
        # Авторизация
        driver.get("http://localhost:8000/login")
        driver.find_element(By.NAME, "username").send_keys("testuser")
        driver.find_element(By.NAME, "password").send_keys("TestPass123!")
        login_button = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Войти')]"))
        )
        login_button.click()

        # Добавление товара в корзину
        first_book = WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.CLASS_NAME, "book-item"))
        )
        add_button = first_book.find_element(By.XPATH, ".//button[contains(text(), 'В корзину')]")
        add_button.click()

        # После добавления в корзину
        WebDriverWait(driver, 15).until(
            EC.invisibility_of_element_located((By.CSS_SELECTOR, ".loading-indicator"))
        )

        # Проверка через JavaScript
        WebDriverWait(driver, 20).until(
            EC.text_to_be_present_in_element(
                (By.XPATH, "//a[contains(@href, 'cart') and contains(., '(1)')]"), 
                "(1)"
            )
        )

        # Вместо этого:
        driver.find_element(By.LINK_TEXT, "Корзина (1)").click()

        # Используйте это:
        WebDriverWait(driver, 15).until(
            EC.element_to_be_clickable((By.XPATH, "//a[contains(@href, 'cart')]"))
        ).click()

    except Exception as e:
        driver.save_screenshot("cart_test_error.png")
        raise e


if __name__ == "__main__":
    pytest.main(["-v", "selenium_tests.py"])