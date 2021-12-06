#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jan 20 2021
@author: louie Zheng
****PRODUCTION VERSION*****

use cmd
python -c "import selenium; print(selenium.__version__)"
3.141.0

pd compare ref
https://www.geeksforgeeks.org/how-to-compare-two-dataframes-with-pandas-compare/

7.0 fix compare fun "Can only compare identically-labeled DataFrame objects"
PRO Production add config ini
"""

from selenium import webdriver
from smtp_test_gmail_html import send_message,send_message_uat
from datetime import datetime
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
import configparser

uatflag=True

#load configure
config = configparser.ConfigParser()
config.read('properties.ini')
target_url=config['PRO']['target_url']
my_path=config['PRO']['my_path']

# then continue your script
# 關閉通知
options = webdriver.ChromeOptions()
prefs = {
    'profile.default_content_setting_values':
        {
            'notifications': 2
        }
}
options.add_experimental_option('prefs', prefs)
options.add_argument("disable-infobars")  

# 打啟動selenium 務必確認driver 檔案跟python 檔案要在同個資料夾中(excute path需放完整路徑包含)
driver = webdriver.Chrome(executable_path=my_path+'chromedriver')
driver.get(target_url)
#time.sleep(5)


source = driver.page_source
soup1 = BeautifulSoup(source)  
ul=soup1.find('ul',{'class':'list-product-block'})


h6=ul.select('li > div.left-part')
ahref=ul.select('li > div.right-part > a.dm-download-block')

#與本地端資料庫中的商品值做比較函式
def merge_url_func(results_for_merge):
    print(pd.__version__)
    # print in tabular format 

    now = datetime.now()
    current_time = now.strftime("%Y-%m-%d %H:%M:%S")
    
    first_df = pd.read_csv(my_path+'transgolbal_origin.csv',encoding = 'utf-8')
    second_df = pd.read_csv(my_path+'transgolbal_tmp.csv',encoding = 'utf-8') 
    
    first_df=first_df.fillna("none") 
    second_df=second_df.fillna("none")
    #first_df.sort_index(axis=1) == second_df.sort_index(axis=1) 
    #np.where(df1 != df2)

    #比對前資料前處理
    first_from=first_df["標題"]+first_df["連結"]
    second_to=second_df["標題"]+second_df["連結"]

    #完全相同
    if first_df.equals(second_df):
        print('Exactly the same.')
        data_str = "排程Complete Time = " + current_time +"\n Exactly the same"
        resul_html="Exactly the same."
        
    #數量相同但值有差異
    elif(first_df.shape==second_df.shape):
        print('somthing difference. type1')
        #compare_result=first_df.compare(second_df)
        compare_result=first_from.compare(second_to)
        compare_result.to_csv(my_path+'compare_result.csv',encoding = 'utf-8')
        resul_html=compare_result.to_html()

        data_str = "排程Complete Time = " + current_time +"\n somthing difference type1:"
         
    #完全相同    
    else:   
        print('somthing difference. type2')
        
        df_result = pd.concat([first_from, second_to], axis='columns', keys=['First', 'Second'])
        #df_final = df_result.swaplevel(axis='columns')[first_df.columns[1:]]
        #轉換NaN避免變數轉換運算錯誤
        df_final=df_result.fillna("none")


        #印出前後不同的地方
        #difference_locations=np.where(first_from != second_to)
        difference_locations=np.where(df_final.iloc[::,0] != df_final.iloc[::,1])
        changed_from = df_final.iloc[::,0].values[difference_locations]
        changed_to = df_final.iloc[::,1].values[difference_locations]
        
        changed=pd.DataFrame({'from': changed_from, 'to': changed_to})
        data_str = "排程Complete Time = " + current_time +"\n somthing difference type2:"
        changed.to_csv(my_path+'changed_result.csv',encoding = 'utf-8')    
        resul_html = changed.to_html() 

    
    
    
    if(uatflag):
        send_message_uat(data_str+"\n",resul_html)
    else:
        send_message(data_str+"\n",resul_html)
    results_for_merge.to_csv(my_path+'transgolbal_origin.csv',encoding = 'utf-8') #存檔  

    

#解析頁面DOM並抓取商品值函式
def crawler_get_productlis(_titles,_links):
    
    productlis=driver.find_elements_by_xpath("//*[@class='list-product-block   space-element-top-default']/li")

    
    for productli in productlis:
        
        source = productli.get_attribute('innerHTML')
        soup2 = BeautifulSoup(source) 
        h6=soup2.find('h6')
        ahref=soup2.find('a',{'class':'dm-download-block'})
        
        
        if ahref is None:   
            titles.append(h6.text) 
            links.append("")
            
        else:   
            titles.append(h6.text)
            links.append(ahref.get('href'))
    
    
    # 將結果做成df
    dictransgolbal = {'標題':titles,
           '連結':links
           }
           
    final_data = pd.DataFrame(dictransgolbal)
    
    return final_data
    # final_data.to_csv('transgolbal.csv',encoding = 'utf-8') #存檔
    # dictransgolbal_tmp = pd.read_csv('transgolbal.csv',encoding = 'utf-8')


#分頁處理
pages=driver.find_elements_by_xpath("//ul[@class='pageNumber pager']/*/a")
counter=0

titles=[] 
links=[] 
print(len(pages))#7

for page in pages:
     pages=driver.find_elements_by_xpath("//ul[@class='pageNumber pager']/*/a")
     print("in page:"+pages[counter].text)
     print(counter)
        
     # On the current page 
     # source = driver.page_source放在迴圈內，否則會一直抓第一頁
     source = driver.page_source
     soup = BeautifulSoup(source)
     
     #for link in soup.find_all('a',{'class':'dm-download-block'}):
        #print(link.get('href'))
        
      
     results=crawler_get_productlis(titles,links)
        
     counter+=1
     if(counter<len(pages)):
         pages[counter].click()   
     #time.sleep(3)

#將結果存檔
results.to_csv(my_path+'transgolbal_tmp.csv',encoding = 'utf-8') #存檔
merge_url_func(results)

driver.close()










