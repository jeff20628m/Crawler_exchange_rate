import selenium
import time
import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver


def chrome_setting():

    options = webdriver.ChromeOptions()
    prefs = {'profile.default_content_setting_values': {'notifications': 2}}
    options.add_experimental_option('prefs', prefs)
    # 關掉瀏覽器左上角的通知提示，如上圖
    options.add_argument("disable-infobars")

    # 關閉'chrome正受到自動測試軟件的控制'提示
    return options


options = chrome_setting()
driver = webdriver.Chrome(chrome_options=options)
driver.get("https://news.cnyes.com/news/cat/forex")


def calendar_select_day(day_now, day_past):  # must put str for date

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


def calender_select_month(month_past):  # input must be '2020 9月'

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


def main_content():

    date = []
    title = []
    category = []
    link = []
    for i in range(1, 10):
        try:
            driver.find_element_by_xpath(
                "//body/div[@id='content']/div[1]/div[1]/div[3]/div[1]/div[1]"
            ).click()
        except selenium.common.exceptions.ElementNotInteractableException:
            driver.execute_script(
                'window.scrollTo(0,document.body.scrollHeight);')
            time.sleep(1)

    soup = BeautifulSoup(driver.page_source, features='lxml')
    for block in soup.find_all("a", class_="_1Zdp"):
        date.append(block.find('time').text)
        title.append(block['title'])
        category.append(block.find(class_="_jFb7 theme-sub-cat").text)
        link.append('https://news.cnyes.com' + block['href'])

    df = pd.DataFrame()

    df['date'] = date
    df['title'] = title
    df['category'] = category
    df['link'] = link

    return df
    