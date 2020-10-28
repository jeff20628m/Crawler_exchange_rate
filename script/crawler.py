import selenium
import time
import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from tqdm import tqdm
import requests


def chrome_setting():

    options = webdriver.ChromeOptions()
    prefs = {
        'profile.default_content_setting_values': {
            'notifications': 2
        },
        'profile.managed_default_content_settings.images': 2
    }
    options.add_experimental_option('prefs', prefs)
    options.add_argument("disable-infobars")
    options.add_argument('headless')
    driver = webdriver.Chrome(options=options)

    return driver


def calendar_select_day(driver, day_now, day_past):  # must put str for date

    try:
        driver.find_element_by_xpath(
            "//body/div[@id='content']/div[1]/div[1]/div[3]/div[1]/div[1]"
        ).click()

    except selenium.common.exceptions.ElementNotInteractableException:
        # this might delete
        # driver.find_element_by_xpath("//body/div[@id='content']/div[1]/div[1]/div[2]/main[1]/div[3]/div[1]/nav[1]/fieldset[1]/input[1]").click()
        # 這個月1號

        for col_place in range(1, 8):
            element = driver.find_element_by_xpath(
                "//body/div[@id='content']/div[1]/div[1]/div[2]/main[1]/div[3]/div[1]/nav[1]/div[1]/div[1]/div[1]/div[2]/div[2]/div[{}]/div[1]"
                .format(col_place))
            if element.text == day_now:
                now_day_click = element
                break
            else:
                pass
        # 上個月1號
        for col_place in range(1, 8):
            element = driver.find_element_by_xpath(
                "//body/div[@id='content']/div[1]/div[1]/div[2]/main[1]/div[3]/div[1]/nav[1]/div[1]/div[1]/div[1]/div[1]/div[2]/div[{}]/div[1]"
                .format(col_place))
            if element.text == day_past:
                past_day_click = element
                break
            else:
                pass

    past_day_click.click()
    now_day_click.click()
    driver.find_element_by_xpath("//button[contains(text(),'確定')]").click()


def calender_select_month(driver, crawler_url,
                          month_past):  # input must be '2020 9月'

    driver.get(crawler_url)

    try:
        driver.find_element_by_xpath(
            "//body/div[@id='content']/div[1]/div[1]/div[3]/div[1]/div[1]"
        ).click()

    except selenium.common.exceptions.ElementNotInteractableException:
        # this might delete
        driver.find_element_by_xpath(
            "//body/div[@id='content']/div[1]/div[1]/div[2]/main[1]/div[3]/div[1]/nav[1]/fieldset[1]/input[1]"
        ).click()

        element = driver.find_element_by_xpath(
            "//body/div[@id='content']/div[1]/div[1]/div[2]/main[1]/div[3]/div[1]/nav[1]/div[1]/div[1]/div[1]/div[1]/div[1]"
        )

        num_click = 0
        while element.text != month_past:
            driver.find_element_by_xpath(
                "//body/div[@id='content']/div[1]/div[1]/div[2]/main[1]/div[3]/div[1]/nav[1]/div[1]/div[1]/div[1]/div[1]/div[1]/div[1]/*[1]"
            ).click()
            num_click += 1
            if num_click == 1000:
                break


def main_content(driver):

    date = []
    title = []
    category = []
    link = []
    for i in tqdm(range(1, 80)):
        try:
            driver.find_element_by_xpath(
                "//body/div[@id='content']/div[1]/div[1]/div[3]/div[1]/div[1]"
            ).click()
        except selenium.common.exceptions.ElementNotInteractableException:
            driver.execute_script(
                'window.scrollTo(0,document.body.scrollHeight);')
            time.sleep(1.5)
            driver.execute_script(
                'window.scrollTo(0,document.body.scrollHeight/1.5);')
            time.sleep(1)

    soup = BeautifulSoup(driver.page_source)
    for block in tqdm(soup.find_all("a", class_="_1Zdp")):
        try:
            driver.find_element_by_xpath(
                "//body/div[@id='content']/div[1]/div[1]/div[3]/div[1]/div[1]"
            ).click()
        except selenium.common.exceptions.ElementNotInteractableException:
            date.append(block.find('time').text)
            title.append(block['title'])
            category.append(block.find(class_="_jFb7 theme-sub-cat").text)
            link.append('https://news.cnyes.com' + block['href'])

    df = pd.DataFrame()

    df['date'] = date
    df['title'] = title
    df['category'] = category
    df['link'] = link

    print("Finish Crawler Content")
    return df


def get_topic_link(driver, crawler_url):

    driver.get(crawler_url)
    time.sleep(2)
    topic_link = {}
    res = requests.get(crawler_url)
    soup = BeautifulSoup(res.text, 'lxml')

    for topic in soup.find_all(class_="_1wbxF"):

        topic_link[topic.find(
            'a')['title']] = 'https://news.cnyes.com' + topic.find('a')['href']

    return topic_link


def crawler_topic(start_date, end_date, topic_link, topic):

    df_total = pd.DataFrame()
    for crawler_date in tqdm(
            pd.date_range(start=start_date, end=end_date, freq='MS')):

        driver = chrome_setting()
        calender_select_month(driver, topic_link[topic],
                              f'{crawler_date.year} {crawler_date.month}月')

        calendar_select_day(driver, '1', '1')

        df = main_content(driver)

        df_total = pd.concat([df_total, df])
        print('========================Finish========================')
        print(crawler_date)
        driver.close()
        time.sleep(0.5)

    return df_total


def crawler_topic_content(df_stock):  # now just for stock

    df = pd.DataFrame()
    reportor = []
    content = []
    stock_name = []
    stock_reference = []
    stock_price = []
    stock_variance = []
    new_reference = []
    new_reference_title = []

    for link in tqdm(df_stock['link']):
        res = requests.get(link)
        soup = BeautifulSoup(res.text, 'lxml')

        try:
            reportor.append(soup.find(class_='_3lKe').text)
        except AttributeError:
            reportor.append('None')
        try:
            content.append(soup.find(class_='_2E8y').text)
        except AttributeError:
            content.append('None')
        try:
            stock_name.append(soup.find(class_="_1FfA")['data-ga-label'])
        except (AttributeError, TypeError):
            stock_name.append('None')
        try:
            stock_reference.append(
                soup.find(class_="_1FfA")['data-proj-ga-action'])
        except (AttributeError, TypeError):
            stock_reference.append('None')
        try:
            stock_price.append(soup.find(class_="_1FfA").find(class_='_37WA'))
        except AttributeError:
            stock_price.append('None')
        try:
            stock_variance.append(
                soup.find(class_="_1FfA").find(class_='_19hX'))
        except AttributeError:
            stock_variance.append('None')
        try:
            new_reference.append(
                soup.find(class_="_3zs-").find('a')['data-proj-ga-action'])
        except (AttributeError, TypeError):
            new_reference.append('None')
        try:
            new_reference_title.append(
                list(
                    map(lambda x: x['title'],
                        soup.find(class_="_3zs-").find_all('a'))))
        except (AttributeError, TypeError):
            new_reference_title.append('None')

    df['date'] = df_stock['date']
    df['title'] = df_stock['title']
    df['category'] = df_stock['category']
    df['reportor'] = reportor
    df['content'] = content
    df['stock_name'] = stock_name
    df['stock_reference'] = stock_reference
    df['stock_price'] = stock_price
    df['stock_variance'] = stock_variance
    df['new_reference'] = new_reference
    df['new_reference_title'] = new_reference_title

    return df
