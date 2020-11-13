from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import requests
driver = webdriver.Chrome()
driver.get('https://www.thingiverse.com/thing:4627293')
timeout = 20
try:
    element_present = EC.presence_of_element_located((By.CLASS_NAME, 'thumbs.animated'))
    WebDriverWait(driver,timeout).until(element_present)
except TimeoutException:
    print ("Timed out waiting for page to load")

imgs = driver.find_elements_by_tag_name('ul')[1].find_elements(By.XPATH, '//li/img')
title = driver.find_element_by_class_name('ThingPage__modelName--3CMsV').get_attribute('innerHTML')
designer = driver.find_element_by_class_name('ThingPage__createdBy--1fVAy').find_element(By.TAG_NAME, 'a')
count = 1
for img in imgs :
    src = img.get_attribute('src')
    if 'youtube' not in src :
        print (src)
        response = requests.get(src)

        with open("images/sku" + str(count), "wb") as file:
            file.write(response.content)
        count = count + 1

print(title)
print(designer.get_attribute('text'))
print(designer.get_attribute('href'))