from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import requests
import requests, zipfile, io
from pathlib import Path
start_range, end_range = input("Please enter start, end of the range to be scapped: ").split()
print(f'starting range at {start_range}\nending range at {end_range}')
driver = webdriver.Chrome()
ALLOWED_LICENSES = [
    'Creative Commons - Attribution',
    'Creative Commons - Attribution - Share Alike',
    'Creative Commons - Attribution - No Derivatives'
]
for id in range(int(start_range), int(end_range)+1):
    if requests.get(f'https://www.thingiverse.com/thing:{id}').status_code != 404:
        driver.get(f'https://www.thingiverse.com/thing:{id}')
        print(f'scraping page with thing = {id}')
        timeout = 20
        try:
            element_present = EC.presence_of_element_located((By.CLASS_NAME, 'thumbs.animated'))
            WebDriverWait(driver,timeout).until(element_present)
        except TimeoutException:
            print ("Timed out waiting for page to load")
        try:
            imgs = driver.find_elements_by_tag_name('ul')[1].find_elements(By.XPATH, '//li/img')
            title = driver.find_element_by_class_name('ThingPage__modelName--3CMsV').get_attribute('innerHTML')
            designer = driver.find_element_by_class_name('ThingPage__createdBy--1fVAy').find_element(By.TAG_NAME, 'a')
            License = driver.find_elements_by_class_name('License__link--NFT8l')[1]
            tags = [ tag.det_attribute('text') for tag in driver.find_elements_by_class_name('Tags__tag--2Rr15')]
        except Exception:
            print ("Faced issues while scraping this page.The content may not be available.")
            continue  
        if License.get_attribute('text') in ALLOWED_LICENSES:  
            continue_scrapping = input(f"Do you want to scrape page with thing = {id}: ")
            if continue_scrapping == 'yes':
                # designer_name = designer.get_attribute('text')
                # count = 1
                # Path(f'./{designer_name}').mkdir(parents=True, exist_ok=True) 
                # for img in imgs :
                #     src = img.get_attribute('src')
                #     if 'youtube' not in src :
                #         response = requests.get(src)

                #         with open(f'{designer_name}/sku{str(count)}', "wb") as file:
                #             file.write(response.content)
                #         count = count + 1

                # print(title)
                # print(designer.get_attribute('text'))
                # print(designer.get_attribute('href'))
                print(License.get_attribute('text'))
                print(License.get_attribute('href'))
    else:
        print(f'page with thing = {id} does not exists.')


def download_zip(url, folder_path):
    print(f'downloading zip from {url}')
    r = requests.get(url)
    if r.status_code == 200:
        z = zipfile.ZipFile(io.BytesIO(r.content))
        z.extractall(folder_path)
        print (f'done downloding file to {folder_path} and zipping it.')
