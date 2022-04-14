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
from time import sleep
from time import time
from random import randint
from warnings import warn
import json

load_dotenv()

def get_article_urls(url):
    # Get the RSS feed
    urls = requests.get(url).text
    parse_url = json.loads(urls) #parses the JSON from urls.
    ## Extracts timestamp and original columns from urls and compiles a url list.
    url_list = []
    for i in range(1,len(parse_url)):
        orig_url = parse_url[i][2]
        tstamp = parse_url[i][1]
        waylink = tstamp+'/'+orig_url
        url_list.append(waylink)
    ## Compiles final url pattern.
    final_url_list= []
    for url in url_list:
        final_url = 'https://web.archive.org/web/'+url
        final_url_list.append(final_url)

    link_array = []
    for link in final_url_list:
        import ssl
        if hasattr(ssl, '_create_unverified_context'):
            ssl._create_default_https_context = ssl._create_unverified_context
            
        second_http =  link.index('/http')
        link =  link[:second_http] + 'if_/' + link[second_http+1:]
        
        
        print(link)
        document = untangle.parse(link)
        items = document.rss.channel.item
        for item in items:
            link = item.link.cdata.split('?')[0]
            link_array.append(link)
    return link_array

def get_article_data(article_url):
    article_html = requests.get(article_url, headers={'User-Agent': 'Custom'}).text
        
    # Parse the HTML
    soup = BeautifulSoup(article_html, 'html.parser')
    #title = soup.find(class_="css-1vkm6nb ehdk2mb0").text
    title = soup.find('meta', {"property":"og:title"})["content"]
    time = soup.find('meta', {"name":"cXenseParse:recs:mdc-changedtime"})['content']
    body_list = []
    body = soup.find('div', class_="text-long")
    for item in body.find_all('p'):
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
    
    
    cna_rss_url = 'http://web.archive.org/cdx/search/cdx?url=channelnewsasia.com/api/v1/rss-outbound-feed?_format=xml&from=20220313&to=20220321&output=json'
    articles = get_article_urls(cna_rss_url)
    print(articles)
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
        jsonFile = open("cna.json", "w")
        jsonFile.write(jsonString)
        jsonFile.close()
    df = pandas.read_json (r'cna.json')
    df.to_csv(r'cna.csv', index = None)
        # update_query = {
        #     'news_outlet': 'cna',
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
    