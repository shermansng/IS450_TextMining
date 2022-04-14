from http import client
from json import load
import pandas
import json
import requests
import untangle
import pymongo
import os
import ssl
from dotenv import load_dotenv
from bs4 import BeautifulSoup

load_dotenv()

#reusable function
def get_article_urls(url):
    # Get the RSS feed
    if hasattr(ssl, '_create_unverified_context'):
        ssl._create_default_https_context = ssl._create_unverified_context
    news_rss = untangle.parse(url)
    # Get the list of articles
    articles = []
    for item in news_rss.rss.channel.item:
        link = item.link.cdata.split('?')[0]
        articles.append(link)
        
    return articles

def bbc_article_data(article_url):
    article_html = requests.get(article_url).text
        
    # Parse the HTML
    soup = BeautifulSoup(article_html, 'html.parser')
    title = soup.find('h1').text
    time = soup.find('time')['datetime']
    
    body_list = []
    for item in soup.find_all('div', class_="ssrcss-uf6wea-RichTextComponentWrapper"):
        body_list.append(item.text+' ')
        
    article_data_obj = {
        'title': title,
        'posted_at': time,
        'body': ' '.join(body_list)
    }
    
    return article_data_obj
    
def cnbc_article_data(article_url):
    article_html = requests.get(article_url).text
    #print(article_url)
        
    # Parse the HTML
    soup = BeautifulSoup(article_html, 'html.parser')
    title = soup.find('title').text
    time = soup.find(itemprop="dateModified")['content']
    
    body_list = []
    childList = []
    li = soup.find_all('div', class_="group")
    for i in li:
        children = i.findChildren("p" , recursive=False)
        childList += children 
    for item in childList:
        body_list.append(item.text+' ')
        
    article_data_obj = {
        'title': title,
        'posted_at': time,
        'body': ' '.join(body_list)
    }
    
    return article_data_obj

def nytimes_article_data(article_url):
    article_html = requests.get(article_url).text
        
    # Parse the HTML
    soup = BeautifulSoup(article_html, 'html.parser')
    #title = soup.find(class_="css-1vkm6nb ehdk2mb0").text
    title = soup.find('title').text.strip(' - The New York Times')
    # time = soup.find('time')['datetime']
    time = soup.find('meta',property="article:modified_time")['content']
    
    body_list = []
    for item in soup.find_all('div', class_="StoryBodyCompanionColumn"):
        body_list.append(item.text+' ')
        
    article_data_obj = {
        'title': title,
        'posted_at': time,
        'body': ' '.join(body_list)
    }
    
    return article_data_obj
    
def washpost_article_data(article_url):
    article_html = requests.get(article_url).text
    
        
    # Parse the HTML
    soup = BeautifulSoup(article_html, 'html.parser')
    # edit the time and datetime
    title = soup.find('title').text.strip(' - The Washington Post')
    time = (soup.find(attrs={"property": "article:modified_time"}))['content']
    
    body_list = []
    for item in soup.find_all('p', class_="font-copy font--article-body gray-darkest ma-0 pb-md"):
        body_list.append(item.text+' ')
        
    article_data_obj = {
        'title': title,
        'posted_at': time,
        'body': ' '.join(body_list)
    }
    
    return article_data_obj
  
def bbc_crawler():
    bbc_rss_url = 'http://feeds.bbci.co.uk/news/rss.xml'
    articles = get_article_urls(bbc_rss_url)
    articleList = []    
    for article in articles:
        article_data_obj = bbc_article_data(article)
        articleJson = {
            'title': article_data_obj['title'],
            'posted_at': article_data_obj['posted_at'],
            'body': article_data_obj['body'],
        }
        articleList.append(articleJson)
        jsonString = json.dumps(articleList)
        jsonFile = open("washpost.json", "w")
        jsonFile.write(jsonString)
        jsonFile.close()
    df = pandas.read_json (r'washpost.json')
    df.to_csv(r'washpost.csv', index = None)

def cnbc_crawler():
    cnbc_rss_url = 'https://search.cnbc.com/rs/search/combinedcms/view.xml?partnerId=wrss01&id=100727362'
    articles = get_article_urls(cnbc_rss_url)   
    articleList = []
    for article in articles:
        article_data_obj = cnbc_article_data(article)
        articleJson = {
                
                'title': article_data_obj['title'],
                'posted_at': article_data_obj['posted_at'],
                'body': article_data_obj['body'],
            }
        articleList.append(articleJson)
        jsonString = json.dumps(articleList)
        jsonFile = open("cnbc.json", "w")
        jsonFile.write(jsonString)
        jsonFile.close()
    df = pandas.read_json (r'cnbc.json')
    df.to_csv(r'cnbc.csv', index = None)

def nytimes_crawler():
    nytimes_rss_url = 'https://rss.nytimes.com/services/xml/rss/nyt/World.xml'
    articles = get_article_urls(nytimes_rss_url)
    articleList = []
    for article in articles:
        article_data_obj = nytimes_article_data(article)
        articleJson = {
                
                'title': article_data_obj['title'],
                'posted_at': article_data_obj['posted_at'],
                'body': article_data_obj['body'],
            }
        articleList.append(articleJson)
        jsonString = json.dumps(articleList)
        jsonFile = open("nytimes.json", "w")
        jsonFile.write(jsonString)
        jsonFile.close()
    df = pandas.read_json (r'nytimes.json')
    df.to_csv(r'nytimes.csv', index = None)

def washpost_crawler():
    washpost_rss_url = 'http://feeds.washingtonpost.com/rss/world?itid=lk_inline_manual_40'
    articles = get_article_urls(washpost_rss_url)
        
    articleList = []
    for article in articles:
        article_data_obj = washpost_article_data(article)
        articleJson = {
                
                'title': article_data_obj['title'],
                'posted_at': article_data_obj['posted_at'],
                'body': article_data_obj['body'],
            }
        articleList.append(articleJson)
        jsonString = json.dumps(articleList)
        jsonFile = open("washpost.json", "w")
        jsonFile.write(jsonString)
        jsonFile.close()
    df = pandas.read_json (r'washpost.json')
    df.to_csv(r'washpost.csv', index = None)


def main():
    #call bbc
    bbc_crawler()
    #call cnbc
    cnbc_crawler()
    #call nytimes
    nytimes_crawler()
    #call washingtonpost
    washpost_crawler()

if __name__ == "__main__":
    main()
    