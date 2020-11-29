import csv
import re
import logging
from random import choice, randint
from json import loads, dump, load
from time import sleep

import requests
from bs4 import BeautifulSoup
from webdriver_manager.firefox import GeckoDriverManager
from webdriver_manager.chrome import ChromeDriverManager
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By

"""
get_contents_div return html code of the url
attributes:
    url - url to source page => string
    delay - time between requests => int
    block_name - search and return this class from source html => string or None
return:
    html source code => string
"""
def get_contents_div(url, delay, block_name):
    user_agents = open('useragents').read().split('\n')
    ua = choice(user_agents)

    proxies = open('proxies').read().split('\n')
    px = choice(proxies)

    logger.info(f'Use proxy: {px}')
    chrome_options = webdriver.ChromeOptions()
    #chrome_options.add_argument('--proxy-server=%s' % px)
    #chrome_options.add_argument(f'user-agent={ua}')
    
    try:
        browser = webdriver.Chrome(options=chrome_options)
    except Exception:
        browser = webdriver.Chrome(ChromeDriverManager().install(), options=chrome_options)
    try:
        browser.get(url)
    except Exception as e:
        logger.error("Exception occurred", exc_info=True)
        
    if (block_name is not None):
        try:
            element_present = EC.presence_of_element_located((By.CLASS_NAME, block_name))
            WebDriverWait(browser, delay).until(element_present)
        except TimeoutException:
            print ("Too long")

    html = browser.page_source
    browser.quit()
    return html

"""
get_links return links to companie page on 2gis
attributes:
    url - url to 2gis page with comnies list => string
    number_of_pages - number of pages to scrape => int
    fname - name of a file where links will be store => string
"""
def get_links(main_url, number_of_pages = 1, fname = "data"):
    for i in range(1, number_of_pages + 1):
        url = main_url + str(i)
        logger.info(f"get_links from {url}")
        html_code = get_contents_div(url, 5, "_awwm2v")
        soup = BeautifulSoup(html_code, 'html.parser')
        links = soup.findAll("a", href=True)
        logger.info(f"{len(links)} links grabbed")
        with open(f"{fname}.csv", 'a', newline='') as fout:
            writer = csv.writer(fout)
            for link in links:
                if '/almaty' in link['href'] and '/search' not in link['href'] and '/directions' not in link['href'] and '/branches' not in link['href']:
                    writer.writerow([link['href']])
        sleep(randint(2, 5))

    logger.info("Links getted succesfully")

"""
get_info function that grabe info about companie and store it in json
attributes:
    fname - name of the file with companies links
"""
def get_info(fname):
    url_main = "https://2gis.kz"
    links = []
    with open('{}.csv'.format(fname)) as f:
        for line in f:
            links.append(line.strip())
    
    for link in links:
        url = url_main + link
        logger.info(f"Scrape from {url}")
        html_code = get_contents_div(url, 10, None)
        regex = r"var initialState = JSON\.parse\('.*}}}'\)"
        matches = re.findall(regex, html_code, re.MULTILINE)
        match = matches[0]
        match = match[31:-2]
        data_dict = loads(match.replace('\\"', " ").replace('\\', ''))

        id = list(data_dict['data']['entity']['profile'].keys())[0]
        with open("rent_places.json", "r") as f:
            rent_places = load(f)

        if id not in rent_places.keys():
            rent_places[id] = data_dict
            with open("cafes.json", "w") as write_file:
                dump(rent_places, write_file)

        logger.info(f"Success added {id}")
        sleep(randint(2, 5))
            

if __name__ == "__main__":
    # create logger
    logger = logging.getLogger('parser.py')
    logger.setLevel(logging.INFO)

    # create console handler and set level to debug
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)

    #create file handler and set level to debug
    fh = logging.FileHandler(r'/logs/app.log')
    fh.setLevel(logging.INFO)

    # create formatte
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # add formatter to ch and fh
    ch.setFormatter(formatter)
    fh.setFormatter(formatter)

    # add ch and fh to logger
    logger.addHandler(ch)
    logger.addHandler(fh)

    #get_links("https://2gis.kz/almaty/search/%D0%9A%D0%B0%D1%84%D0%B5/rubricId/161/page/", 10, "cafes_links")
    #get_info("cafes_links")
