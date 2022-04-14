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

def get_article_urls(url):
    # Get the RSS feed
    if hasattr(ssl, '_create_unverified_context'):
        ssl._create_default_https_context = ssl._create_unverified_context
    nytimes_rss = untangle.parse(url)
    # Get the list of articles
    articles = []
    for item in nytimes_rss.rss.channel.item:
        link = item.link.cdata.split('?')[0]
        articles.append(link)
        
    return articles
    

def get_article_data(article_url):
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
    
    
    nytimes_rss_url = 'https://rss.nytimes.com/services/xml/rss/nyt/World.xml'
    articles = get_article_urls(nytimes_rss_url)
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
        jsonFile = open("nytimes.json", "w")
        jsonFile.write(jsonString)
        jsonFile.close()
    df = pandas.read_json (r'nytimes.json')
    df.to_csv(r'nytimes.csv', index = None)
        # update_query = {
        #     'news_outlet': 'nytimes',
        #     'title': article_data_obj['title'],
        #     'posted_at': article_data_obj['posted_at'],
        # }
        # # print(article_data_obj)
        # update_data = {
        #     '$set': {
        #         'body': article_data_obj['body']
        #     }
        # }
        
        # db.articles.update_one(update_query, update_data, upsert=True)


if __name__ == "__main__":
    main()
    