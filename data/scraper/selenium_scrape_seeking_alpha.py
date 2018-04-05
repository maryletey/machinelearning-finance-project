from selenium import webdriver
import csv
import requests
import time
from lxml import html
from google_search import GoogleDriver
import sys

def clean_xpath(r):
    return clean_str(r[0].text_content())

def clean_str(s):
    return s.replace('\n', '')

def get_xpath(xp, tree):
    return clean_xpath(tree.xpath(xp))

def parse_seeking_alpha(driver):
    try:
        title = driver.find_element_by_xpath("//h1[@itemprop='headline']")
        title = clean_str(title.text)
        date = driver.find_element_by_xpath("//time[@itemprop='datePublished']")
        date = clean_str(date.text)
        body = driver.find_element_by_xpath("//div[@itemprop='articleBody']")
        body = clean_str(body.text)
        return (title, date, body)
    except:
        return None
        
def parse_fool(driver):
    try:
        title = driver.find_element_by_xpath("//header/h1")
        title = clean_str(title.text)
        date = driver.find_element_by_xpath("//div[@class='publication-date']")
        date = clean_str(date.text)
        body = driver.find_element_by_xpath("//span[@class='article-content']")
        body = clean_str(body.text)
        return (title, date, body)
    except:
        return None

def parse_wsj(driver):
    try:
        title = driver.find_element_by_xpath("//h1[@itemprop='headline']")
        title = clean_str(title.text)
        date = driver.find_element_by_xpath("//time[@class='timestamp']")
        date = clean_str(date.text)
        try:
            body = driver.find_element_by_xpath("//div[@itemprop='articleBody']")
        except:
            body = driver.find_element_by_xpath("//div[@class='wsj-snippet-body']")
            
        body = clean_str(body.text)
        return (title, date, body)
    except:
        return None

def parse_page(url, time_delay=20):
    driver = None
    try:
        driver = webdriver.Firefox()
        driver.get(url)
        if "seekingalpha" in url:
            title, date, body =  parse_seeking_alpha(driver)
        elif "wsj.com" in url:
            title, date, body = parse_wsj(driver)
        elif "fool.com" in url:
            title, date, body = parse_fool(driver)

        driver.close()
        time.sleep(time_delay)                
        return (title, date, body)
    except:
        if driver:
            driver.close()
            time.sleep(time_delay)                
        return None

def read_all_links(fn, col=0):
    urls = []
    with open(fn, 'r') as csvfile:
        reader = csv.DictReader(csvfile)
        fieldname = reader.fieldnames[col]
        for row in reader:
            urls.append(row[fieldname])
    return urls

def eprint(*args):
    print(*args, file=sys.stderr)

def url_to_initial_state(url):
    return (url,0,None)
    
def attempt_page_scrape(url, delay=20):
    try:
        title, date, body = parse_page(url,delay)
        return (title, date, body)
    except Exception as e:
        eprint("Failed for url: {} with reason: {}".format(url, e))
        return None


def attempt_with_state(stateful_url, delay=20):
    url, attempts, result = stateful_url
    if result == None:
        result = attempt_page_scrape(url, delay)
    return (url, attempts + 1, result)
    

if __name__ == '__main__':
    query = sys.argv[1]
    date_ranges = [('1/1/2013', '6/1/2013'),
                   ('6/2/2013', '1/1/2014'),
                   ('1/2/2014', '6/1/2014'),
                   ('6/2/2014', '1/1/2015'),
                   ('1/2/2015', '6/1/2015'),
                   ('6/2/2015', '1/1/2016'),
                   ('1/2/2016', '6/1/2016'),
                   ('6/2/2016', '1/1/2017'),
                   ('1/2/2017', '6/1/2017'),
                   ('6/2/2017', '1/1/2018'),
                   ('1/2/2018', '6/1/2018')]

    urls = []
    for frm, to in date_ranges:
        try:
            gdriver = GoogleDriver(query, 2)
            gdriver.filter_date_range(frm, to)
            for page in gdriver:
                urls += gdriver.page_urls()
            gdriver.close()
        except:
            eprint("Failed for date range ({}, {})".format(frm,to))

    stateful_urls = map(url_to_initial_state, urls)
    for i in range(3):
        delay = 7 * (i+1)
        stateful_urls = map(lambda t: attempt_with_state(t, delay), stateful_urls)

    with sys.stdout as csvfile:
        fieldnames = ['title', 'date', 'body']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for _, _, result in stateful_urls:
            if result:
                title, date, body = result
                #eprint("title: {}, date: {}".format(title, date))
                writer.writerow({'title': title, 'date': date, 'body': body})
