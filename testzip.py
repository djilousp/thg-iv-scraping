import requests, zipfile, io
import concurrent.futures 
urls = [
    "https://www.thingiverse.com/thing:4627300/zip",
    "https://www.thingiverse.com/thing:4627293/zip"
]
folder_paths = ['f1', 'f2']
def download_zip(url, folder_path):
    print(f'downloading zip from {url}')
    r = requests.get(url)
    if r.status_code == 200:
        z = zipfile.ZipFile(io.BytesIO(r.content))
        z.extractall(folder_path)
        print (f'done downloding file to {folder_path} and zipping it.')


with concurrent.futures.ThreadPoolExecutor() as exector : 
    exector.map(download_zip, urls, folder_paths)