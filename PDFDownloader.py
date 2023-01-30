from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os
import time
import csv


class PDFDownloader:
    def __init__(self, input_path):
        self.input_path = input_path
        self.asignaturas = self.read_csv_to_csv()

    def read_csv_to_csv(self):
        d = []
        with open(self.input_path, 'r') as file:
            reader = csv.reader(file)
            for row in reader:
                d.append(row)
        return d

    def main(self):
        self.iniciar_driver()
        for asignatura in self.asignaturas:
            print(asignatura[0])
            self.download_pdfs(asignatura[1], asignatura[0])

    def iniciar_driver(self):
        chrome_options = webdriver.ChromeOptions()
        prefs = {"download.default_directory": f"{os.getcwd()}\\pdfs",
                 "download.prompt_for_download": False,  # To auto download the file
                 "download.directory_upgrade": True,
                 "plugins.always_open_pdf_externally": True  # It will not show PDF directly in chrome
                 }
        chrome_options.add_experimental_option("prefs", prefs)

        # Iniciar el navegador
        self.driver = webdriver.Chrome(chrome_options=chrome_options)

    def download_pdfs(self, pdf_url, asignatura):
        # Iniciar sesión
        self.driver.get(pdf_url)
        wait = WebDriverWait(self.driver, 20)
        wait.until(EC.url_to_be(pdf_url[1:]))


        # Obtener el código HTML de la página de PDFs
        self.driver.get(pdf_url)
        html = self.driver.page_source

        pdf_links = self.get_pdf_links(html, asignatura)
        self.create_folder_temp()

        for link in pdf_links:
            os.makedirs(link[1], exist_ok=True)
            print(f'link {link[2]} descargandose')
            self.driver.get(link[0])
            files = os.listdir(f'{os.getcwd()}\\pdfs')
            while ((any(elem for elem in files if ".tmp" in elem)) or
                   (any(elem for elem in files if ".crdownload" in elem))):
                files = os.listdir(f'{os.getcwd()}\\pdfs')
                print(files)
                time.sleep(1)
            print(files)
            if len(files) != 0:
                extension = os.path.splitext(files[0])[1]
                if extension not in ('.tgz'):
                    print(extension)
                    old = os.path.join(f'{os.getcwd()}\\pdfs', files[0])
                    new = os.path.join(f'{link[1]}', f'{link[2]}{extension}')
                    os.rename(old, new)
                    print(f'complete download')
                    for root, dirs, files in os.walk("pdfs", topdown=False):
                        for name in files:
                            os.remove(os.path.join(root, name))
                        for name in dirs:
                            os.rmdir(os.path.join(root, name))


    def create_folder_temp(self):
        if not os.path.exists("pdfs"):
            os.mkdir("pdfs")
        else:
            for root, dirs, files in os.walk("pdfs", topdown=False):
                for name in files:
                    os.remove(os.path.join(root, name))
                for name in dirs:
                    os.rmdir(os.path.join(root, name))

    def get_pdf_links(self, html, Asignatura):
        soup = BeautifulSoup(html, "html.parser")
        pdfs_links = []
        for link in soup.find_all(class_="section main clearfix"):
            path = f'{os.getcwd()}\\{Asignatura}'
            apartado1 = link.find(class_='summary').find('h1')
            apartado1 = apartado1.text if (apartado1 is not None) else ''
            apartado1 = apartado1.replace(':', '')
            path += f'\\{apartado1}'
            prev_path = path
            tag = False
            new_path = path
            for link in link.find(class_='section img-text').find_all('li'):
                if link.get('class') is not None:
                    if 'label' in link.get('class'):
                        if not tag:
                            prev_path = new_path
                            if link.text is not '':
                                new_path += f'\\{link.text}'
                        else:
                            if link.text is not '':
                                new_path = prev_path + f'\\{link.text}'
                            tag = False
                    if (('resource' in link.get('class')) and
                            ('label' not in link.get('class'))):
                        tag = True

                    for link in link.find_all("a", href=True):
                        if 'mod/resource/' in link["href"] and 'Archivo' in link.text:
                            pdfs_links.append((link['href'], new_path,
                                               str(link.text).replace(' Archivo', '').replace(':', '').replace('/', '.').replace('"', '')))
                            tag = True
        return pdfs_links



PDF = PDFDownloader(f"{os.getcwd()}\\Entradas_2.csv")
print(PDF.asignaturas)
pdf_url = "https://aulaglobal.uc3m.es/course/view.php?id=158262"
PDF.main()
