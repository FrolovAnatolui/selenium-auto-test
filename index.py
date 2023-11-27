from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import configparser
import sys

# Загрузка данных из файла conf.ini
configFilename = './start-configs/conf.ini'
config = configparser.ConfigParser()
config.read(configFilename)

# Переменные конфига
timeout = config.get("case", "timeout")
timeout_2 = config.get("case", "timeout_2")
browser = config.get("case", 'browser')
search_string = config.get("case", 'search_string')
article = config.get("case", 'article')
expected_title_1 = config.get("case", 'expected_title_1')
expected_title_2 = config.get("case", 'expected_title_2')

# Инициализация веб-драйвера
if browser == 'chrome':
    driver = webdriver.Chrome()
elif browser == 'firefox':
    driver = webdriver.Firefox()
else:
    print('Браузер не предусмотрен')
    sys.exit(1)  # Выход из программы при неподдерживаемом браузере

# Получаем текущее время в формате Unix timestamp
current_time = int(time.time())

# Создаем имя файла на основе времени
log_filename = f"logs/{current_time}.log"

# Открываем файл для записи
with open(log_filename, "w") as log_file:
    log_file.write("Результаты операций скрипта.")

# Перенаправляем вывод в файл
sys.stdout = open(log_filename, 'a')

try:
    # Шаг 1: Выполнить поиск документов по фразе «нк ч2».
    driver.get("https://www.consultant.ru/cons/")
    search_box = driver.find_element(By.CLASS_NAME, "x-input__field")
    search_box.send_keys(search_string)
    search_box.send_keys(Keys.RETURN)

    # Пауза для ожидания загрузки результатов
    time.sleep(5)

    # Шаг 2: Открыть первый документ из списка результатов поиска.
    result_element = WebDriverWait(driver, timeout).until(
        EC.presence_of_element_located((By.CLASS_NAME, "x-page-search-plus-results__list"))
    )

    links_with_data_index = result_element.find_elements(By.CSS_SELECTOR, '[data-index]')
    if links_with_data_index:
        first_link = links_with_data_index[0]
        first_link.click()

except Exception as e:
    print(f"Ошибка на шаге 1: {str(e)}")

# Шаги 3 и 4
try:
    WebDriverWait(driver, timeout).until(
        EC.number_of_windows_to_be(2)
    )
    all_handles = driver.window_handles
    new_tab_handle = all_handles[1]
    driver.switch_to.window(new_tab_handle)
    print(f"\nДокумент загружен менее, чем за {timeout} секунд:")

    if expected_title_1.lower() in driver.title.lower():
        print(f"\nЗаголовок новой вкладки содержит '{expected_title_1}'")
    else:
        print(f"\nЗаголовок новой вкладки не содержит '{expected_title_1}'")

    if expected_title_2.lower() in driver.title.lower():
        print(f"\nЗаголовок новой вкладки содержит '{expected_title_2}'")
    else:
        print(f"\nЗаголовок новой вкладки не содержит '{expected_title_2}'")

except Exception as e:
    print(f"\nОшибка на шагах 3 и 4: {str(e)}")

# Шаг 5
try:
    dict_element = WebDriverWait(driver, timeout).until(
        EC.visibility_of_element_located((By.ID, "dictFilter"))
    )

    WebDriverWait(driver, 10).until(
        EC.text_to_be_present_in_element_value((By.ID, "dictFilter"), "")
    )

    value = dict_element.get_attribute("value")
    if "нк ч2" in value:
        print(f"\nВ панели «Поиск в тексте» находится поисковая фраза «нк ч2».")
    else:
        print(f"\nВ панели «Поиск в тексте» не находится поисковая фраза «нк ч2».")

except Exception as e:
    print(f"\nОшибка на шаге 5: {str(e)}")

contents_element = WebDriverWait(driver, timeout).until(
    EC.visibility_of_element_located((By.CLASS_NAME, "contents"))
)
contents_element.click()


time.sleep(5)  
try:
    # Нахождение поля поиска и ввод значения
    search_input = WebDriverWait(driver, timeout).until(
        EC.visibility_of_element_located((By.CLASS_NAME, "x-input__field"))
    )
    search_input.send_keys(article)
    search_input.send_keys(Keys.RETURN)

    # Ожидание, пока элемент станет кликабельным
    article_element = WebDriverWait(driver, timeout_2).until(
        EC.element_to_be_clickable((By.CLASS_NAME, "x-list__item--current"))
    )
    article_element.click()


except Exception as e:
    print(f"\nОшибка: {str(e)}")




# Восстанавливаем sys.stdout на стандартный вывод
sys.stdout = sys.__stdout__

# Пауза перед завершением
time.sleep(60)

# Закрытие браузера
driver.quit()
