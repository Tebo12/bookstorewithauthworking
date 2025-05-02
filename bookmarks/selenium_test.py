from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time
import random


TEST_USER = f"testuser{random.randint(1000,9999)}"
TEST_PASS = "TestPass123!"
TEST_EMAIL = f"{TEST_USER}@example.com"

def main():
    try:
        #Настройка драйвера
        options = webdriver.ChromeOptions()
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        
        driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=options
        )
        
        #Тест регистрации
        driver.get("http://localhost:8000/register/")
        
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "id_username"))
        ).send_keys(TEST_USER)
        
        driver.find_element(By.ID, "id_email").send_keys(TEST_EMAIL)
        driver.find_element(By.ID, "id_password").send_keys(TEST_PASS)
        driver.find_element(By.ID, "id_confirm_password").send_keys(TEST_PASS)
        driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()

        #Проверка успешной регистрации
        WebDriverWait(driver, 10).until(
            EC.url_contains("/login/")
        )
        print("Регистрация прошла успешно")

        #явное ожидание элементов формы входа
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "input[name='username']"))
        )

        #Заполнение формы входа
        username_field = driver.find_element(By.CSS_SELECTOR, "input[name='username']")
        password_field = driver.find_element(By.CSS_SELECTOR, "input[name='password']")
        
        username_field.send_keys(TEST_USER)
        password_field.send_keys(TEST_PASS)
        
        #Клик по кнопке с текстом "Войти"
        driver.find_element(By.XPATH, "//button[contains(text(), 'Войти')]").click()

        #Проверка успешного входа по наличию кнопки выхода
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//a[contains(text(), 'Выйти')]"))
        )
        print("Авторизация прошла успешно")

        #Тест заказа
        first_book = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".book-item .button.orange"))
        )
        first_book.click()
        
        driver.get("http://localhost:8000/cart/")
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.LINK_TEXT, "Оформить заказ"))
        ).click()
        
        print("заказ успешно оформлен")
        
    except Exception as e:
        driver.save_screenshot("error.png")
        print(f"Ошибка: {str(e)}")
    finally:
        driver.quit()

if __name__ == "__main__":
    main() 