import os
import time
import urllib.request
import webbrowser
from gateway import db
from models import Mesaj, Modem
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.options import Options


# status modem : stopped, running, busy
# stopped : modemul nu a pornit, stare initala
# running : modemul este pornit si asteapta joburi
# busy : modemul proceseaza joburi

counter = 0
page_selector = 'body > mw-app > div > main > mw-authentication-container > div > div > div > div.qr-code-container > div.qr-code-wrapper > mw-qr-code > img'
qr_selector = 'body > mw-app > div > main > mw-authentication-container > div > div > div > div.qr-code-container > div.qr-code-wrapper > mw-qr-code > img'
loader_selector = 'loader'
chat_button_selector = 'body > mw-app > div > main > mw-main-container > div > mw-main-nav > div > mw-fab-link > a'
input_number_selector = ''
input_message_selector = 'body > mw-app > div > main > mw-main-container > div.main-container > mw-conversation-container > div > div > mws-message-compose > div > div.input-box > div > mws-autosize-textarea > textarea'

def counter_numar():
    global counter
    counter += 1

class Webdriver:
    def __init__(self, site_url, name):
        self.generateBrowser(name)
        self.letssee(site_url)
    def generateBrowser(self, name):
        curent_path = os.getcwd()  # preluam directorul curent
        # definim driverul pentru selenium
        driver_path = curent_path + '/tools/drivers/chromedriver.exe'
        # definim directorul pentru profilul driverului
        user_data_dir = curent_path + '/tools/%s' % name
        options = webdriver.ChromeOptions()
        options.add_argument('--user-data-dir={}'.format(user_data_dir))
        # options.add_argument('--headless')
        options.add_argument('--disable-extensions')
        options.add_argument('--disable-gpu')
        options.add_argument("--window-size=800,600")


        self.driver = webdriver.Chrome(
            executable_path=driver_path, options=options)
        self.driver.set_page_load_timeout(5)
        modem1 = Modem.query.filter_by(name='google_message_web').first()
        modem1.status = 'stopped'
        db.session.commit()

    def letssee(self, site_url):
        #validari modemul

        self.driver.get(site_url)
        time.sleep(5)
        if (self.driver.find_elements_by_css_selector(page_selector)):
            # preluam codul qr
            img = self.driver.find_element_by_css_selector(qr_selector)
            timestamp = time.strftime('%d-%m-%Y %H-%M-%S')
            src = img.get_attribute('src')
            qr_image_url = '/static/qr'+timestamp+'.png'
            urllib.request.urlretrieve(src, os.getcwd()+qr_image_url)
            # Asteptam 120 de secunde sa dispara codul qr
            print('Preluam codul qr')
            try:
                print('Nu este logat contul, Scanati codul qr : Aveti la dispozitie 2 minute')
                no_login = WebDriverWait(self.driver, 10).until(
                    EC.invisibility_of_element_located((By.CSS_SELECTOR, qr_selector))
                )
                try:
                    # Asteptam sa dispara elementul loader
                    startpage = WebDriverWait(self.driver, 10).until(
                        EC.invisibility_of_element_located((By.ID, 'loader'))
                    )
                    # print('Am gasit elementul'+ str(startpage))
                    print('Pagina este gata')
                except TimeoutException:
                    print('Pagina nu este gata')
                    self.driver.quit()


            except TimeoutException:
                print('Prima pagina nu a fost incarcata')
                self.driver.quit()
            else:
                # nu exista cod qr - contul este logat si asteptam sa se inchida elementul loader
                try:
                    # Asteptam sa dispara elementul loader
                    startpage = WebDriverWait(self.driver, 10).until(
                        EC.invisibility_of_element_located((By.ID, loader_selector))
                    )
                    # print('Am gasit elementul'+ str(startpage))
                    print('Pagina este gata')
                except TimeoutException:
                    print('Pagina nu este gata')
        print('Am terminat initializarea')
        modem1 = Modem.query.filter_by(name='google_message_web').first()
        modem1.status = 'running'
        db.session.commit()



    def letsclose(self):
        self.driver.quit()
        modem1 = Modem.query.filter_by(name='google_message_web').first()
        modem1.status = 'stopped'
        db.session.commit()

def send_sms(nume, nr_telefon, mesaj):
    modem1 = Modem.query.filter_by(name='google_message_web').first()
    modem1.status = 'busy'
    db.session.commit()
    time.sleep(10)
    try:
        start_chat = WebDriverWait(myWebsite.driver, 30).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, chat_button_selector))
        )
        print('dam clik pe startchat')
        start_chat.click()
    except TimeoutException:
        print('nu pot sa dau click')
        myWebsite.letsclose()

    nr_telefon = str(nr_telefon)
    nr_telefon = nr_telefon[0:10]+'\n'
    try:
        input_number = WebDriverWait(myWebsite.driver, 10).until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, '#mat-chip-list-%d > div > input' % counter))
        )
        print(nume + ' cu numarul: ' + nr_telefon + ' primeste mesajul: ' + mesaj)
        input_number.send_keys(nr_telefon)

    except TimeoutException:
        print('Ceva nu a mers bine: Nu pot sa introduc numarul de telefon')
        myWebsite.letsclose()
    counter_numar()
    mesaj = str(mesaj)
    input_text = WebDriverWait(myWebsite.driver, 5).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, input_message_selector))
    )
    input_text.send_keys(mesaj+'\n')
    print('am terminat de scris')
    time.sleep(10)

def mesaj_watch():
    modem1 = Modem.query.filter_by(name='google_message_web').first()
    mesaje_netrimise = Mesaj.query.filter_by(is_sent=False).all()
    if mesaje_netrimise and modem1.status == 'running':
        for mesaj in mesaje_netrimise:

            send_sms(mesaj.name, mesaj.telefon, mesaj.mesaj)
            mesaj.date_sent = datetime.utcnow()
            mesaj.is_sent = True
            db.session.commit()
            time.sleep(2)
        modem1 = Modem.query.filter_by(name='google_message_web').first()
        modem1.status = 'running'
        db.session.commit()
        return "<a href='/'>am trimis ceva... cred</a>"
    elif modem1.status != 'running':
        return "<a href='/'>Modemul nu este pornit </a>"
    else:
        return "nu pot trimite nimic"

url1 = 'https://messages.google.com/web/conversations'
myWebsite = Webdriver(url1, 'google')
myWebsite.driver
