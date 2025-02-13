from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, StaleElementReferenceException
import pandas as pd
import time
import random
import logging

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def setup_driver():
    """
    Настройка и запуск драйвера Chrome.

    Возвращает:
    webdriver.Chrome: экземпляр драйвера Chrome с настроенными параметрами.
    """
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920x1080")
    options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36"
    )
    return webdriver.Chrome(options=options)

def scroll_and_load(driver):
    """
    Прокручивает страницу несколько раз для загрузки всех динамических элементов.

    Параметры:
    driver (webdriver.Chrome): экземпляр драйвера Chrome.
    """
    for _ in range(3):
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(random.uniform(2, 4))

def extract_all_products_info(driver):
    """
    Извлекает информацию о всех продуктах на странице.

    Параметры:
    driver (webdriver.Chrome): экземпляр драйвера Chrome.

    Возвращает:
    list: список словарей, каждый из которых содержит информацию о продукте.
    """
    products_info = []
    wait = WebDriverWait(driver, 10)
    
    try:
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "a.app-catalog-9gnskf.e1259i3g0")))
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "button > span > div.app-catalog-14zo1we.e1yq4jy70 > span > span > span.e1j9birj0.e106ikdt0.app-catalog-56qww8.e1gjr6xo0")))
        
        name_elements = driver.find_elements(By.CSS_SELECTOR, "a.app-catalog-9gnskf.e1259i3g0")
        price_elements = driver.find_elements(By.CSS_SELECTOR, "button > span > div.app-catalog-14zo1we.e1yq4jy70 > span > span > span.e1j9birj0.e106ikdt0.app-catalog-56qww8.e1gjr6xo0")

        logger.info(f"Найдено наименований: {len(name_elements)}, цен: {len(price_elements)}")

        for i in range(max(len(name_elements), len(price_elements))):
            try:
                name = name_elements[i].text.strip() if i < len(name_elements) else "Название не указано"
                price = price_elements[i].text.strip() if i < len(price_elements) else "Цена не указана"
                products_info.append({"Наименование": name, "Цена": price})
                logger.debug(f"Добавлен товар: {name} - {price}")
            except (StaleElementReferenceException, IndexError) as e:
                logger.warning(f"Ошибка при обработке элемента {i}: {e}")

        logger.info(f"Всего обработано товаров: {len(products_info)}")

    except TimeoutException:
        logger.error("Превышено время ожидания загрузки элементов")
    except NoSuchElementException as e:
        logger.error(f"Ошибка при извлечении данных: {e}")
    except Exception as e:
        logger.error(f"Произошла непредвиденная ошибка: {e}")

    return products_info

def scrape_page(driver, url, page_number):
    """
    Парсит отдельную страницу.

    Параметры:
    driver (webdriver.Chrome): экземпляр драйвера Chrome.
    url (str): URL страницы для парсинга.
    page_number (int): номер страницы.

    Возвращает:
    list: список словарей, каждый из которых содержит информацию о продукте на странице.
    """
    driver.get(url)
    scroll_and_load(driver)
    return extract_all_products_info(driver)

def main():
    """
    Основная функция для выполнения скрапинга.
    """
    driver = setup_driver()
    base_url = input("Введите базовый URL сайта: ")
    total_pages = int(input("Введите количество страниц для обработки: "))
    data = []

    try:
        for page_number in range(1, total_pages + 1):
            url = f"{base_url}&p={page_number}"
            page_data = scrape_page(driver, url, page_number)
            data.extend(page_data)
            print(f"Страница {page_number} обработана. Получено {len(page_data)} товаров.")
            time.sleep(random.uniform(1, 3))
    finally:
        driver.quit()

    df = pd.DataFrame(data)
    df.to_excel("output.xlsx", index=False)
    print(f"Данные успешно экспортированы в файл output.xlsx. Всего обработано {len(data)} товаров.")

if __name__ == "__main__":
    main()