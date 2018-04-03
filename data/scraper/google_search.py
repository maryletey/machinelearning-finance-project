from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import urllib
import time

class GoogleDriver(webdriver.Firefox):

    def __init__(self, query, max_page = 3):
        webdriver.Firefox.__init__(self)
        self.get('https://www.google.com')
        self.max_page = 3
        self.cur_page = 0
        self.query = query
        self.__search_for(query)

    def __search_for(self, query):
        search_box = self.find_element_by_id("lst-ib")
        search_box.send_keys(query)
        time.sleep(1)
        search_btn = self.find_element_by_xpath("//input[@value='Google Search']")
        time.sleep(1)
        search_btn.click()
        time.sleep(1)

    def __open_tools_menu(self):
        tools_btn = self.find_element_by_id("hdtb-tls")
        time.sleep(1)
        tools_btn.click()
        time.sleep(1)

    def __open_date_selector(self):
        self.__open_tools_menu()
        time_selector = self.find_element_by_xpath("//div[text()='Any time']")
        time.sleep(1)
        time_selector.click()
        time.sleep(1)
        cust_range_selector = self.find_element_by_xpath("//span[text()='Custom range...']")
        time.sleep(1)
        cust_range_selector.click()
        time.sleep(1)
        
    def filter_date_range(self, frm, to):
        self.__open_date_selector()
        from_box = self.find_element_by_id('cdr_min')
        time.sleep(1)
        from_box.send_keys(frm)
        time.sleep(1)
        to_box = self.find_element_by_id('cdr_max')
        time.sleep(1)
        to_box.send_keys(to)
        time.sleep(1)
        to_box.send_keys(Keys.ENTER)
        time.sleep(1)

    def page_urls(self):
        search_results = self.find_elements_by_xpath("//div[@class='rc']")
        clean_urls = []
        for result in search_results:
            a_elm = result.find_element_by_xpath(".//a")
            ugly_url = a_elm.get_attribute("href")
            unquoted = urllib.parse.unquote(ugly_url)
            url_idx = unquoted.find("url=")
            clean_urls.append(unquoted[url_idx+1:])
        return clean_urls

    def next_page(self):
        next_page_btn = self.find_element_by_xpath(".//*[@id='pnnext']/span[2]")
        next_page_btn.click()
        self.cur_page += 1 
        time.sleep(5)

    def __iter__(self):
        return self

    def __next__(self):
        if self.cur_page > self.max_page:
            raise StopIteration

        if self.cur_page == 0:
            self.cur_page = 2
        else:
            try:
                self.next_page()
            except:
                raise StopIteration
        return self
