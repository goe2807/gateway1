import os
import time
import urllib.request
import webbrowser
from flask import Flask, redirect, url_for
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException

app = Flask(__name__)
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 1
curent_path = os.getcwd()  # preluam directorul curent
driver_path = curent_path + '/tools/chromedriver.exe'  # definim driverul pentru selenium
user_data_dir = curent_path + '/tools/User Data/'  # definim directorul pentru profilul driverului
options = webdriver.ChromeOptions()
options.add_argument('--user-data-dir={}'.format(user_data_dir))
# options.add_argument('--headless')
options.add_argument('--disable-extensions')
options.add_argument('--disable-gpu')
options.add_argument("--window-size=800,600")

app_url = 'https://messages.google.com/web/conversations'  # adresa site-ului
counter = 0  # counterul de mesaje trimise - se foloseste de google la input number -se incrementeaza cu +1
# selectors
page_selector = 'body > mw-app > div > main > mw-authentication-container > div > div > div > div.qr-code-container > div.qr-code-wrapper > mw-qr-code > img'
qr_selector = 'body > mw-app > div > main > mw-authentication-container > div > div > div > div.qr-code-container > div.qr-code-wrapper > mw-qr-code > img'
loader_selector = 'loader'
chat_button_selector = 'body > mw-app > div > main > mw-main-container > div.main-container > mw-main-nav > div > mw-fab-link > a'
input_number_selector = ''
input_message_selector = 'body > mw-app > div > main > mw-main-container > div.main-container > mw-conversation-container > div > div > mws-message-compose > div > div.input-box > div > mws-autosize-textarea > textarea'

driver = webdriver.Chrome(executable_path=driver_path, options=options)


def close_app(object):
    object.close()
    print('Inchidem aplicatia')
    print('Goodbye')
    exit()


def counter_numar():
    global counter
    counter += 1


@app.route('/')
def hello_world():

    return "Hello World! apasa aici : \
            <a href='/sendsms'>Pornim Scriptul de sms</a>"


@app.route('/sendsms')
def send_sms():
    # try:
    #     browser.get('https://www.hotnews.ro')
    #     browser.get_screenshot_as_file("static/screenshot4.png")
    #     browser.get('https://www.cancan.ro')
    #     browser.get_screenshot_as_file("static/screenshot3.png")
    #     return redirect(url_for('view_shot'))
    # finally:
    #     print('am facut ceva')
    global app_url
    print('incarcam pagina')
    driver.set_page_load_timeout(1)
    print(app_url)
    driver.get(app_url)
    time.sleep(5)
    if (driver.find_elements_by_css_selector(page_selector)):
        # preluam codul qr
        img = driver.find_element_by_css_selector(qr_selector)
        timestamp = time.strftime('%d-%m-%Y %H-%M-%S')
        src = img.get_attribute('src')
        qr_image_url = '/static/qr'+timestamp+'.png'
        urllib.request.urlretrieve(src, os.getcwd()+qr_image_url)
        # Asteptam 120 de secunde sa dispara codul qr
        try:
            print('Nu este logat contul, Scanati codul qr : Aveti la dispozitie 2 minute')
            no_login = WebDriverWait(driver, 120).until(
                EC.invisibility_of_element_located((By.CSS_SELECTOR, qr_selector))
            )
            try:
                # Asteptam sa dispara elementul loader
                startpage = WebDriverWait(driver, 10).until(
                    EC.invisibility_of_element_located((By.ID, 'loader'))
                )
                # print('Am gasit elementul'+ str(startpage))
                print('Pagina este gata')
            except TimeoutException:
                print('Pagina nu este gata')
                close_app(driver)

        except TimeoutException:
            print('Prima pagina nu a fost incarcata')
            close_app(driver)
        else:
            # nu exista cod qr - contul este logat si asteptam sa se inchida elementul loader
            try:
                # Asteptam sa dispara elementul loader
                startpage = WebDriverWait(driver, 10).until(
                    EC.invisibility_of_element_located((By.ID, loader_selector))
                )
                # print('Am gasit elementul'+ str(startpage))
                print('Pagina este gata')
            except TimeoutException:
                print('Pagina nu este gata')
                close_app(driver)
        print('Am terminat initializarea')
    return redirect(url_for('view_shot'))


def trimite_sms(nr_telefon, mesaj):
    try:
        start_chat = WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, chat_button_selector))
        )
        # print(str(start_chat))
        print('dam clik pe startchat')
        start_chat.click()
    except TimeoutException:
        print('nu pot sa dau click')
        close_app(driver)

    nr_telefon = str(nr_telefon)
    nr_telefon = nr_telefon[0:10]+'\n'
    # print('Scriem numarul' + nr_telefon)
    try:
        input_number = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, '#mat-chip-list-%d > div > input' % counter))
        )
        print('scriem textul pentru ' + nr_telefon)
        input_number.send_keys(nr_telefon)

    except TimeoutException:
        print('Ceva nu a mers bine: Nu pot sa introduc numarul de telefon')
        close_app()
    counter_numar()
    # input_number.send_keys(nr_telefon)

    # print('scriem textul pentru ' + nr_telefon)
    mesaj = str(mesaj)  # trebuie sa adaugam + '\n' pentru a trimite mesajul scris

    input_text = WebDriverWait(driver, 5).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, input_message_selector))
    )
    input_text.send_keys(mesaj+'\n')
    print('am terminat de scris')
    time.sleep(1)


@app.route('/show')
def view_shot():
    return "<a href='/test'>Fa un test</a>"


@app.route('/test')
def send_test():
    trimite_sms('0774622315', 'Acesta este un test')
    return "<a href='/'>Pagina Principala</a>"


if __name__ == '__main__':
    url = 'http://127.0.0.1:5000'
    webbrowser.open_new(url)
    app.run()
