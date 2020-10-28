from crawler import (chrome_setting, get_topic_link, crawler_topic,
                     crawler_topic_content)
import time

driver = chrome_setting()

time.sleep(2)
topic_link = get_topic_link(driver, 'https://news.cnyes.com')
driver.close()
df_stock = crawler_topic(start_date='2019/1/1',
                         end_date='2019/7/1',
                         topic_link=topic_link,
                         topic='台股')

#df_stock.to_csv('./data/TW_STOCK_NEWS.csv', index=False)

df_content = crawler_topic_content(df_stock)

df_content.to_csv('./data/TW_STOCK_NEWS.csv', index=False)
