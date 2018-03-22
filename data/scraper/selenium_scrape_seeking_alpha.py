from selenium import webdriver
import csv
import requests
import time
from lxml import html

def clean_xpath(r):
    return clean_str(r[0].text_content())

def clean_str(s):
    return s.replace('\n', '')

def get_xpath(xp, tree):
    return clean_xpath(tree.xpath(xp))

def parse_page(url):
    driver = None
    try:
        driver = webdriver.Firefox()
        driver.get(url)
        title = driver.find_element_by_xpath("//h1[@itemprop='headline']")
        title = clean_str(title.text)
        date = driver.find_element_by_xpath("//time[@itemprop='datePublished']")
        date = clean_str(date.text)
        body = driver.find_element_by_xpath("//div[@itemprop='articleBody']")
        body = clean_str(body.text)

        driver.close()
        return (title, date, body)
    except:
        if driver:
            driver.close()
        return None

def read_all_links(fn, col=0):
    urls = []
    with open(fn, 'r') as csvfile:
        reader = csv.DictReader(csvfile)
        fieldname = reader.fieldnames[col]
        for row in reader:
            urls.append(row[fieldname])
    return urls

if __name__ == '__main__':
    urls = read_all_links('links/all_ibm_seekingalpha_links.csv')
    with open('seeking_alpha_page_data.csv', 'w') as csvfile:
        fieldnames = ['title', 'date', 'body']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for url in urls:
            try:
                title, date, body = parse_page(url)
                print("title: {}, date: {}".format(title, date))
                writer.writerow({'title': title, 'date': date, 'body': body})
            except Exception as e:
                print(e)
            time.sleep(10)                
