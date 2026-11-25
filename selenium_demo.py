from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from pathlib import Path
with webdriver.Chrome() as driver:
    driver.get('http://127.0.0.1:5000')
    driver.find_element(By.CSS_SELECTOR,'button[type=submit]').click()
    WebDriverWait(driver,10).until(EC.text_to_be_present_in_element((By.ID,'result'),'FLOOD | ON TIME'))
    Path('evidence').mkdir(exist_ok=True)
    driver.save_screenshot('evidence/selenium.png')
    print('PASS: flood alert flow')
