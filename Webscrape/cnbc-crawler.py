from http import client
from json import load
import json 
import pandas
import requests
import untangle
import pymongo
import os
import ssl
from dotenv import load_dotenv
from bs4 import BeautifulSoup

load_dotenv()

def get_article_urls(url):
    # Get the RSS feed
    if hasattr(ssl, '_create_unverified_context'):
        ssl._create_default_https_context = ssl._create_unverified_context
    cnbc_rss = untangle.parse(url)
    # Get the list of articles
    articles = []
    for item in cnbc_rss.rss.channel.item:
        link = item.link.cdata.split('?')[0]
        articles.append(link)
        
    return articles
    

def get_article_data(article_url):
    article_html = requests.get(article_url).text
    print(article_url)
        
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
    

    
# def create_collections(client, db_name, collections):
#     db = client[db_name]
#     db_collections = set(db.list_collection_names())
#     collections = set(collections)
#     for collection in collections - db_collections:
#         db.create_collection(collection)
        

def main():
    # client = pymongo.MongoClient(os.environ.get('MONGO_URI'))
    # db_name = os.environ['MONGO_DB']
    # db = client[db_name]
    
    # collections = ['articles']
    # create_collections(client, db_name, collections)
    
    
    cnbc_rss_url = 'https://search.cnbc.com/rs/search/combinedcms/view.xml?partnerId=wrss01&id=100727362'
    articles = get_article_urls(cnbc_rss_url)
        
    articleList = []
    for article in articles:
        article_data_obj = get_article_data(article)
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
        # update_query = {
        #     'news_outlet': 'cnbc',
        #     'title': article_data_obj['title'],
        #     'posted_at': article_data_obj['posted_at'],
        # }
        
        # update_data = {
        #     '$set': {
        #         'body': article_data_obj['body']
        #     }
        # }
        
        # db.articles.update_one(update_query, update_data, upsert=True)


if __name__ == "__main__":
    main()
    