
from big_seo.crawler.search_engine import GoogleCSE, GoogleCSEParser
from big_seo.crawler.proxy_service import NoneProxy
from big_seo.storage.db_io import (NoneDBWebPageDataController,
                                   MongoWebPageDataController,
                                   connect_db)
from big_seo.storage.mongo_data_model import WebPageMongo

from big_seo.crawler.app import GGCrawler
from dotenv import load_dotenv
import uvicorn
from fastapi import FastAPI
import sys
import os
import uuid

load_dotenv(r'D:\workspace\engineering\seo_creator\.env')


# Create a FastAPI instance

app = FastAPI()

proxy = NoneProxy()
connect_db()
web_page_data_controller = MongoWebPageDataController()
search_engine = GoogleCSE(proxy=proxy,
                          parser=GoogleCSEParser(),
                          web_page_data_controller=web_page_data_controller)

crawler = GGCrawler(search_engine=search_engine,
                    db_io_controller=web_page_data_controller,
                    proxy=proxy)

# Define a root `/` endpoint


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/search")
async def search(q: str, n: int):
    # crawler.crawl(keyword=q, number_of_pages=n)
    return list(map(lambda x: x.full_content, crawler.crawl(keyword=q, number_of_pages=n)))


@app.get("/search-doc")
async def search(domain: str):
    # crawler.crawl(keyword=q, number_of_pages=n)
    return uuid.UUID(bytes=WebPageMongo.objects(domain=domain).first().page_id)


# Run the API with uvicorn

if __name__ == "__main__":
    uvicorn.run("api:app", port=5000, log_level="info")
