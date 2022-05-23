
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
import time
import re
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup as bs
import requests
import random


# url_bp = r'https://www.linkedin.com/jobs/search/?f_C=1389%2C1391&geoId=92000000'
url_bp=r'https://www.linkedin.com/company/bp/jobs/'

wd= webdriver.Chrome(executable_path='C:\chromedriver.exe')

# Login
wd.get(url_bp)
time.sleep(5)
wd.find_element(By.CSS_SELECTOR,'#main-content > div > form > p > button').click()
# elem = wd.find_element_by_css_selector('#session_key')
elem = wd.find_element(by=By.CSS_SELECTOR, value= '#session_key')
elem.send_keys('username')
# elem = wd.find_element_by_css_selector('#session_password')
elem = wd.find_element(By.CSS_SELECTOR,value = '#session_password')
elem.send_keys('password')
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



class shell:
    
    def __init__(self, page_number) -> None:
        self.page_number = page_number
    
    def make_soup(self,url):
    # parse a html page for analysis with bs4
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.129 Safari/537.36'}
        cookies = {
            'Cookie': 'BAIDUID=A467EBC2C2D0C1F5CE71C86F2D851B89:FG=1; PSTM=1569895226; BIDUPSID=9BD73512109ADEBC79D0E6031A361FF2; ab_jid=3401447befc2a1f1fb58e1332e7a70a45049; ab_jid=3401447befc2a1f1fb58e1332e7a70a45049; ab_jid_BFESS=3401447befc2a1f1fb58e1332e7a70a45049; BDORZ=B490B5EBF6F3CD402E515D22BCDA1598'}
        text = requests.get(url, headers=headers, cookies=cookies, verify=True).text
        soup = bs(text, features='lxml')
        return soup

    def get_links_in_a_page(self,url):
        '''
        The function gets all the links in a page
        '''
        soup = self.make_soup(url)
        links_raw =[ item['href'] for item in soup.find_all(class_= r'\"background__white', href=True)]
        links = [r'https://jobs.shell.com'+link[2:][:-2] for link in links_raw] 
        return links

    def page_urls_generator(self):
        '''
        The function is to get all the urls, one url for each page
        '''
        urls=[]
        from_str= r'https://jobs.shell.com/search-jobs/results?ActiveFacetID=0&CurrentPage='
        end_str =r'&RecordsPerPage=15&Distance=50&RadiusUnitType=0&Keywords=&Location=&ShowRadius=False&IsPagination=False&CustomFacetName=&FacetTerm=&FacetType=0&SearchResultsModuleName=Search+Results&SearchFiltersModuleName=Search+Filters&SortCriteria=0&SortDirection=0&SearchType=5&PostalCode=&fc=&fl=&fcf=&afc=&afl=&afcf='
        for i in range(1,self.page_number +1):
            urls.append(from_str+str(i)+end_str)
        return urls

    def job_links_generator(self):
        urls = self.page_urls_generator()
        links = []
        for url in urls:
            links = links + self.get_links_in_a_page(url)
        return links


    def extract_job_info_in_description_page_v2(self,page_url):
        soup = self.make_soup(page_url)
        info = soup.find('div', attrs={'class':'job-info__wrapper bottom-border__red'}).find_all('span', attrs={'class':'job-info__content'})
        label = soup.find('div', attrs={'class':'job-info__wrapper bottom-border__red'}).find_all('span', attrs={'class':'job-info__label'})

        try:
            Job_title = soup.find('h1',attrs={'class':'heading__job-title'}).text
        except:
            Job_title = 'N/A'

        try:
            job_description = soup.find('div', attrs={'class':'ats-description__feed-content'}).text
        except:
            job_description = 'N/A'

        info_count = len(label)

        job_dict_1={}
        for i in range(0,info_count):
            try:
                job_dict_1[label[i].text]=info[i].text
            except:
                job_dict_1[label[i].text]='N/A'
        
        location_info = soup.find_all('span', attrs={'class':'job-location-info__content'})
        location_label = soup.find_all('span', attrs={'class':'job-location-info__label'})
        
        location_count = len(location_info)

        job_dict_2 = {}
        for i in range(0,location_count):
            try:
                job_dict_2[location_label[i].text] = location_info[i].text
            except:
                job_dict_2[location_label[i].text] = 'N/A'
        
        job_entry_dict = {'Job title':Job_title}
        job_entry_dict.update(job_dict_1)
        job_entry_dict.update(job_dict_2)
        job_entry_dict['Job description'] = job_description
        job_entry_dict['Job link']=page_url
        job_entry = pd.DataFrame.from_dict(job_entry_dict, orient='index').T 

        return job_entry   

    def data_extraction(self):
        urls= self.job_links_generator()
        # links = []
        # for url in urls:
        #     links.append(job_links_generator())
        Job_data = pd.DataFrame()
        for url in urls:
            job_entry = self.extract_job_info_in_description_page_v2(url)
            Job_data = pd.concat([Job_data,job_entry])
        return Job_data
    
    
    import pandas as pd
from bs4 import BeautifulSoup as bs
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
import time
import random

# url_search_results = r'https://krb-sjobs.brassring.com/tgnewui/search/home/home?partnerid=30080&siteid=6558#keyWordSearch='

driver = webdriver.Chrome(executable_path='C:\chromedriver.exe')

class total:
    

    def __init__(self, driver) -> None:
        self.url_search_page =r'https://krb-sjobs.brassring.com/tgnewui/search/home/home?partnerid=30080&siteid=6558#home'
        self.driver = driver      
    

    def get_the_job_links(self):

        self.driver.get(self.url_search_page)
        time.sleep(5)

        # click the search button to get the list of jobs
        self.driver.find_element(By.CSS_SELECTOR,'#searchControls_BUTTON_2 > span.ladda-label').click()
        time.sleep(10)

        # scroll to the bottom
        try:
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        except:
            time.sleep(10)
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

        # click all the 'show more jobs' to get the full list of jobs
        try:
            while True:
                self.driver.find_element(By.CSS_SELECTOR, '#showMoreJobs').click()
                time.sleep(2)
        except:
            pass

        # get the links for each job
        items = driver.find_elements(By.CSS_SELECTOR,'[class = "jobProperty jobtitle"]')
        links = [item.get_attribute('href') for item in items]
    
        return links


    def extract_info_from_page(self,url):
        self.driver.get(url)
        try:
            elem = self.driver.find_element(By.CSS_SELECTOR, '#content > div.homeContentLiner > div.clearfix.homeContent.MainContent')
        except:
            time.sleep(55+random.randint(3,10))
            self.driver.get(url)
            elem = self.driver.find_element(By.CSS_SELECTOR, '#content > div.homeContentLiner > div.clearfix.homeContent.MainContent')
        try:
            items = elem.find_elements(By.CSS_SELECTOR, '#content > div.homeContentLiner > div.clearfix.homeContent.MainContent > div:nth-child(4) > div.clearfix.jobDetailsMainDiv.ng-scope > div > div.questionClass.ng-scope > div')
        except:
            pass
        # items_count = len(items)

        job_entry_dict={}
        for item in items[8:]:
            try:
                job_entry_dict[item.text.split('\n')[0]] = item.text.split('\n')[1]
            except:
                pass
        
        try:
            job_description = elem.find_element(By.CSS_SELECTOR, '#content > div.homeContentLiner > div.clearfix.homeContent.MainContent > div:nth-child(4) > div.clearfix.jobDetailsMainDiv.ng-scope > div > div.questionClass.ng-scope > div:nth-child(6)').text
        except:
            job_description='N/A'
        try:
            job_title = elem.find_element(By.CSS_SELECTOR, '#content > div.homeContentLiner > div.clearfix.homeContent.MainContent > div:nth-child(4) > div.clearfix.jobDetailsMainDiv.ng-scope > div > div.questionClass.ng-scope > div:nth-child(2) > span > h1').text
        except:
            job_title = 'N/A'
        # try: 
        #     location = elem.find_element(By.CSS_SELECTOR, '#content > div.homeContentLiner > div.clearfix.homeContent.MainContent > div:nth-child(4) > div.clearfix.jobDetailsMainDiv.ng-scope > div > div.questionClass.ng-scope > div:nth-child(10) > p.answer.ng-scope.section2LeftfieldsInJobDetails').text
        # except:
        #     location = 'N/A'
        try: 
            country = elem.find_element(By.CSS_SELECTOR, '#content > div.homeContentLiner > div.clearfix.homeContent.MainContent > div:nth-child(4) > div.clearfix.jobDetailsMainDiv.ng-scope > div > div.questionClass.ng-scope > div:nth-child(5) > p').text
        except:
            country = 'N/A'
        try:
            post_date = elem.find_element(By.CSS_SELECTOR, '#content > div.homeContentLiner > div.clearfix.homeContent.MainContent > div:nth-child(4) > div.clearfix.jobDetailsMainDiv.ng-scope > div > div.questionClass.ng-scope > div:nth-child(1) > p').text
        except:
            post_date = 'N/A'
        
        job_entry_dict_2 =    {
            'Job title' :   job_title,
            'Country'   :   country,
            'Post date' : post_date,
            'Job description': job_description
        }
        job_entry_dict.update(job_entry_dict_2)
        job_entry_dict['Job link'] = url

        job_entry = pd.DataFrame.from_dict(job_entry_dict, orient='index').T 

        return job_entry


    def get_all_post_data(self):
        links = self.get_the_job_links()

        data = pd.DataFrame()

        for link in links:
            page_data = self.extract_info_from_page(link)
            data = pd.concat([data, page_data])
            time.sleep(random.randint(4,10))
        return data


