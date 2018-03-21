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

def parse_page(data):
    tree = html.fromstring(data)
    
    title = get_xpath("//h1[@itemprop='headline']", tree)
    date = get_xpath("//time[@itemprop='datePublished']", tree)
    body = get_xpath("//div[@itemprop='articleBody']", tree)
    return (title, date, body)

def read_all_links(fn, col=0):
    urls = []
    with open(fn, 'r') as csvfile:
        reader = csv.DictReader(csvfile)
        fieldname = reader.fieldnames[col]
        for row in reader:
            urls.append(row[fieldname])
    return urls

if __name__ == '__main__':
    urls = read_all_links('google_links.csv')
    with open('seeking_alpha_page_data.csv', 'w') as csvfile:
        fieldnames = ['title', 'date', 'body']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for url in urls:
            # Have to spoof user agent because they don't like bots
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:20.0) Gecko/20100101 Firefox/20.0'}
            resp = requests.get(url, headers=headers)
            try:
                title, date, body = parse_page(resp.content)
                writer.writerow({'title': title, 'date': date, 'body': body})
            except Exception as e:
                print(e)
                print(resp.text)
            time.sleep(15)                
