
import pandas as pd
# from bs4 import BeautifulSoup as bs
from selenium import webdriver
from selenium.webdriver.common.by import By
import time
import re
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys


# url_bp = r'https://www.linkedin.com/jobs/search/?f_C=1389%2C1391&geoId=92000000'
url_bp=r'https://www.linkedin.com/company/bp/jobs/'

wd= webdriver.Chrome(executable_path='C:\chromedriver.exe')

# Login
wd.get(url_bp)
time.sleep(5)
wd.find_element(By.CSS_SELECTOR,'#main-content > div > form > p > button').click()
# elem = wd.find_element_by_css_selector('#session_key')
elem = wd.find_element(by=By.CSS_SELECTOR, value= '#session_key')
elem.send_keys('kovkov@163.com')
# elem = wd.find_element_by_css_selector('#session_password')
elem = wd.find_element(By.CSS_SELECTOR,value = '#session_password')
elem.send_keys('2022@ihs')
wd.find_element(By.CSS_SELECTOR, value='#main-content > div > div > div > form > button').click()

# Get to the job page
wd.get(url_bp)
wd.find_element(By.CSS_SELECTOR, value='#main > div.org-grid__content-height-enforcer > div > section > div > div > a').click()

for handle in wd.window_handles:
    wd.switch_to.window(handle)
    if 'Search all Jobs' in wd.title:
        break
Job_list_window = wd.current_window_handle

# scroll to the bottom


def get_page_info_v2(wd,url):
    wd.get(url)
    # list_items = wd.find_elements_by_class_name("occludable-update")
    list_items = wd.find_elements(By.CSS_SELECTOR, value = '.occludable-update')
    # job_info = wd.find_elements(By.CLASS_NAME,value = 'jobs-search-results__list-item')
    # block = wd.find_element(By.CSS_SELECTOR,'body > div.application-outlet > div.authentication-outlet > div.job-search-ext > div.jobs-search-two-pane__wrapper > div > section.jobs-search__left-rail > div > div > ul')
    # code = block.get_attribute('innerHTML')
    # job_id = re.findall('<div data-job-id="(\d*)"',code)

    position = []
    company =[]
    location = []
    details = []    

    #if it's the last page, the last item of list_items cannot be used.
    if len(list_items) < 25:
        list_items.pop()
    else:
        pass

    for job in list_items:
    # executes JavaScript to scroll the div into view
        wd.execute_script("arguments[0].scrollIntoView();", job)
        job.click()
        time.sleep(3)
        # get info:
        # [position, company, location] = job.text.split('\n')[:3]
        position_text = job.text.split('\n')[0]
        company_text = job.text.split('\n')[1]
        location_text = job.text.split('\n')[2]

        if len(position_text) == 0:
            position.append('N/A')
        else:
            position.append(position_text)

        if len(company_text) == 0:
            company.append('N/A')
        else:
            company.append(company_text)            
        
        if len(location_text) == 0:
            location.append('N/A')
        else:
            location.append(location_text)
        # position.append(job.text.split('\n')[0])
        # company.append(job.text.split('\n')[1])
        # location.append(job.text.split('\n')[2])
        detail = wd.find_element_by_id("job-details").text
        if len(detail) == 0:
            details.append('N/A')
        else:
            details.append(detail)

    # temp = pd.DataFrame({'Job id':job_id,'Job title':position, 'Job location':location, 'Company': company, 'Details':details}) 
    temp = pd.DataFrame({'Job title':position, 'Job location':location, 'Company': company, 'Details':details}) 
    return temp



def get_page_info(wd,url):
    wd.get(url)
    ac = ActionChains(wd)
    ac.move_to_element(wd.find_element(By.ID,'ember126')).perform()
    random_number = 5
    # job_info = wd.find_elements_by_class_name('jobs-search-results__list-item')
    job_info = wd.find_elements(By.CLASS_NAME,value = 'jobs-search-results__list-item')
    # ac.move_to_element(wd.find_element(By.ID,'compactfooter-copyright')).perform()
    time.sleep(10)
    job_title=[]
    location = []
    company = []
    for title in job_info:
        job_title.append(title.text.split('\n')[0])
        company.append(title.text.split('\n')[1])
        location.append(title.text.split('\n')[2])
        wd.implicitly_wait(random_number)
        time.sleep(random_number)

        left_rail = wd.find_element(By.CSS_SELECTOR,'.jobs-search__left-rail')
        wd.implicitly_wait(2)
        time.sleep(3)
        left_rail.send_keys(Keys.PAGE_DOWN)

    block = wd.find_element(By.CSS_SELECTOR,'body > div.application-outlet > div.authentication-outlet > div.job-search-ext > div.jobs-search-two-pane__wrapper > div > section.jobs-search__left-rail > div > div > ul')
    code = block.get_attribute('innerHTML')

    job_id = re.findall('<div data-job-id="(\d*)"',code)
    # job_title=re.findall('disabled ember-view job-card-container__link job-card-list__title">\n              (.*?)\n            </a>',code)
    # location = re.findall('job-card-container__metadata-item">(.*?)</li>',code)

    temp = pd.DataFrame({'Job id':job_id,'Job title':job_title, 'Job location':location, 'Company': company}) 

    return temp  
# ac.move_to_element(wd.find_element(By.ID,'compactfooter-copyright')).perform()

def bp_url_generator(page):
    url_bp_list=['https://www.linkedin.com/jobs/search/?f_C=1389%2C1391&geoId=92000000']
    bp_url_base = r'https://www.linkedin.com/jobs/search/?f_C=1389%2C1391&geoId=92000000&start='

    for i in range(1,page):
        url =bp_url_base+ str(i*25)
        url_bp_list.append(url)
    return url_bp_list


company_base_urls ={
    'bp':'https://www.linkedin.com/jobs/search/?f_C=1389%2C1391&geoId=92000000',
    'Shell':'https://www.linkedin.com/jobs/search/?f_C=1271%2C28446844%2C41804%2C28452536&geoId=92000000'
}

def company_jobs_url_generator(base_url,page_number):
    url_list = [base_url]
    url_from_page_2 = base_url + '&start='
    for i in range(1,page_number):
        url = url_from_page_2 + str(i*25)
        url_list.append(url)
    return url_list
        


table = pd.DataFrame()

shell_url_list = company_jobs_url_generator(company_base_urls['Shell'],40)

for url in shell_url_list[0:5]:
    temp = get_page_info_v2(wd,url)
    table = pd.concat([table,temp])

table.to_excel('Shell data to page 5.xlsx')

for url in shell_url_list[5:10]:
    temp = get_page_info_v2(wd,url)
    table = pd.concat([table,temp])

table.to_excel('Shell data to page 10.xlsx')


for url in shell_url_list[10:15]:
    temp = get_page_info_v2(wd,url)
    table = pd.concat([table,temp])

table.to_excel('Shell data to page 15.xlsx')

for url in shell_url_list[15:20]:
    temp = get_page_info_v2(wd,url)
    table = pd.concat([table,temp])

table.to_excel('Shell data to page 20.xlsx')

for url in shell_url_list[20:25]:
    temp = get_page_info_v2(wd,url)
    table = pd.concat([table,temp])

table.to_excel('Shell data to page 25.xlsx')

# For the data scraping with a few pages for each try
url_list = bp_url_generator(27)
for url in url_list[0:5]:
    temp = get_page_info_v2(wd,url)
    table = pd.concat([table,temp])

table.to_excel('bp data to page 5.xlsx')


for url in url_list[5:10]:
    temp = get_page_info_v2(wd,url)
    table = pd.concat([table,temp])

table.to_excel('bp data to page 10.xlsx')
    

for url in url_list[10:15]:
    temp = get_page_info_v2(wd,url)
    table = pd.concat([table,temp])

table.to_excel('bp data to page 15.xlsx')

for url in url_list[15:20]:
    temp = get_page_info_v2(wd,url)
    table = pd.concat([table,temp])

table.to_excel('bp data to page 20.xlsx')

for url in url_list[20:]:
    temp = get_page_info_v2(wd,url)
    table = pd.concat([table,temp])

table.to_excel('bp data full.xlsx')