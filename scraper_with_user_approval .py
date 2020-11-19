import io
import re
import os
import shutil
import zipfile
import pandas as pd
from pathlib import Path

import requests
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager

def remove_unnecessary_files(folder_path):
    ALLOWED_EXTENSIONS = ['stl', 'obj', 'gcode']
    #remove images folder
    files = os.listdir(folder_path)
    if 'images' in files :
        shutil.rmtree(f'{folder_path}/images/')
    #remove unallowed files
    for f in files:
        if os.path.isfile(os.path.join(folder_path, f)):
            os.remove(f'{folder_path}/{f}')
    full_path= f'{os.getcwd()}\\{folder_path}\\files\\'
    files = os.listdir(full_path)
    stl_files = [f for f in files if '.stl' in f ]
    obj_files = [f for f in files if '.obj' in f ]
    gcode_files = [f for f in files if '.gcode' in f ]
    if len(stl_files) > 1: 
        count = 1
        for f in stl_files:  
            os.rename(full_path + f, f'{full_path + folder_path + str(count)}.stl')
            count = count + 1
    if len(stl_files) > 1: 
        count = 1
        for f in obj_files:  
            os.rename(full_path + f, f'{full_path + folder_path + str(count)}.obj')
            count = count + 1 
    if len(stl_files) > 1: 
        count = 1
        for f in gcode_files:  
            os.rename(full_path + f, f'{full_path + folder_path + str(count)}.gcode')
            count = count +1 

    for f in files :
        if f.split('.')[-1].lower() not in ALLOWED_EXTENSIONS:
            os.remove(full_path + f)
    
def download_zip(url, folder_path):
    print(f'[+] Downloading zip from {url}')
    r = requests.get(url)
    if r.status_code == 200:
        z = zipfile.ZipFile(io.BytesIO(r.content))
        z.extractall(folder_path)
        print(f'[+] Finished downloding and unzipping file to {folder_path}.')
        for root, subFolder, files in os.walk(f'{os.getcwd()}/{folder_path}'):
            for item in files:
                if os.path.isfile(os.path.join(root,item)):
                    if str(item) not in os.listdir(folder_path):
                        shutil.move(os.path.join(root,item), f'{os.getcwd()}/{folder_path}')
                    else:
                        os.remove(os.path.join(root,item))

        for root, subFolder, files in os.walk(f'{os.getcwd()}/{folder_path}'):
            for subf in subFolder: 
                shutil.rmtree(os.path.join(root,subf))
        Path(f'./{folder_path}/files').mkdir(parents=True, exist_ok=True)
        files = [ name for name in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, name))]
        for f in files: 
            shutil.move(os.path.join(f'{os.getcwd()}/{folder_path}',f), f'{os.getcwd()}/{folder_path}/files')
        # remove images folder and unnecessary files
        remove_unnecessary_files(folder_path)



start_range, end_range = input(
    "Please enter start, end of the range to be scapped: ").split()
print(f'starting range at :{start_range}\nend of range :{end_range}')
options = webdriver.ChromeOptions()
options.add_argument('--ignore-certificate-errors') 
options.add_argument('--ignore-ssl-errors')
driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)
#driver = webdriver.Chrome()

ALLOWED_LICENSES = [
    'Creative Commons - Attribution',
    'Creative Commons - Attribution - Share Alike',
    'Creative Commons - Attribution - No Derivatives',
]
products = {}
product_num = 0
alarm = 0 
for id in range(int(start_range), int(end_range)+1,-1):
    url = f'https://www.thingiverse.com/thing:{id}'
    if requests.get(url).status_code != 404:
        driver.get(url)
        print(f'[+] Scrapping page with thing = {id}.....')
        timeout = 20
        try:
            element_present = EC.presence_of_element_located(
                (By.CLASS_NAME, 'thumbs.animated'))
            WebDriverWait(driver, timeout).until(element_present)
        except TimeoutException:
            print("Timed out waiting for page to load")
        try:
            imgs = driver.find_elements_by_tag_name(
                'ul')[1].find_elements(By.XPATH, '//li/img')
            License = driver.find_elements_by_class_name(
                'License__link--NFT8l')[1]
        except Exception:
            print(
                "Faced issues while scrapping this page.The content may not be available.")
            continue

        print(f"Product License :{License.get_attribute('text')}")
        if License.get_attribute('text') in ALLOWED_LICENSES:
            if not alarm  :
                os.system("alarm.mp3")
                alarm = True
            # remove user approval !
            continue_scrapping = input(f"Do you want to continue [y/n] : ")
            if continue_scrapping in ['y', 'Y']:
                product_name = driver.find_element_by_class_name(
                    'ThingPage__modelName--3CMsV').get_attribute('innerHTML')
                product_name = re.sub('[^A-Za-z0-9]+', '', product_name)
                designer = driver.find_element_by_class_name(
                    'ThingPage__createdBy--1fVAy').find_element(By.TAG_NAME, 'a')
                designer_name = designer.get_attribute('text')
                designer_attribute_link = designer.get_attribute('href')
                tags = ', '.join([tag.get_attribute('text') for tag in driver.find_elements_by_class_name('Tags__tag--2Rr15')])
                TAG_RE = re.compile(r'<[^>]+>')
                summary = re.sub(TAG_RE,'', driver.find_element_by_css_selector('div.ThingPage__description--14TtH').find_element(By.TAG_NAME, 'div').get_attribute('innerHTML'))
                description = summary + '\n' + '\n'.join([re.sub(TAG_RE, '', description.get_attribute('innerHTML')) for description in driver.find_elements_by_xpath("//p[@class='ThingPage__description--14TtH']")])
                count = 1
                folder_name = sku = product_name.split('(')[0].replace(" ", "").lower()
                Path(f'./{folder_name}').mkdir(parents=True, exist_ok=True)
                download_zip(url+'/zip', folder_name)
                Path(f'./{folder_name}/images').mkdir(parents=True, exist_ok=True)
                for img in imgs:
                    src = img.get_attribute('src')
                    if 'youtube' not in src:
                        response = requests.get(src)
                        with open(f'{folder_name}/images/{folder_name + str(count)}.jpg', "wb") as file:
                            file.write(response.content)
                        count = count + 1
                product_num = product_num + 1 
                products[product_num] = [product_name, url, designer_name, designer_attribute_link, description, tags, sku]
                products_df = pd.DataFrame.from_dict(products, orient='index', columns = ['Product Name', 'Product URL' ,'Designer Name', 'Designer Attribute Link', 'Description', 'Tags', 'SKU'])
                products_df.to_csv('products.csv')
    else:
        print(f'page with thing = {id} does not exists.')
# products_df = pd.DataFrame.from_dict(products, orient='index', columns = ['Product Name', 'Product URL' ,'Designer Name', 'Designer Attribute Link', 'Description', 'Tags', 'SKU'])
# products_df.to_csv('products.csv')