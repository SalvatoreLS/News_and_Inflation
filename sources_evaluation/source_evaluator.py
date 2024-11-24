import fitz
import re
import requests

import numpy as np
import pandas as pd

import json

import os
from dotenv import load_dotenv
from scrapegraphai.graphs import SmartScraperGraph
from scrapegraphai.utils import prettify_exec_info

from urllib.parse import urlparse, urljoin
from urllib.robotparser import RobotFileParser


class SourceEvaluator():
  def __init__(self, pdf_path, links=None, api_key_=None):
    self.pdf_path = pdf_path
    self.links = links
    self.cleaned = False
    self.groq_api_key = api_key_

    self.graph_config = {
        "llm": {
            "model": "groq/gemma-7b-it",
            "api_key": self.groq_api_key,
            "temperature": 0
        },
        "headless": False,
    }

  def get_links(self):
    self.links = {"website": [],
           "url": []}
    
    document = fitz.open(self.pdf_path)

    for page_number in range(len(document[3:10])):
        page = document[page_number]
        links = page.get_links()

        if links:
            for link in links:
                url = link.get("uri", None)

                rect = link.get("from")

                if rect:
                    anchor_text = page.get_textbox(rect)
                else:
                    anchor_text = None

                if url:
                    self.links["website"].append(anchor_text)
                    self.links["url"].append(url)

    self.links = pd.DataFrame(self.links)
  

  def clean_website_name(self):

    if self.cleaned:
      return

    pattern = r"\b[a-zA-Z]+\b"

    for i in range(len(self.links)):
        words = re.findall(pattern, self.links.loc[i, "website"])
        
        self.links.loc[i, "website"] = " ".join(words)

    self.cleaned = True

  
  def can_scrape(self, url):

    try:
      # Parse the base URL
      parsed_url = urlparse(url)
      base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"
      
      # Construct the robots.txt URL
      robots_url = urljoin(base_url, "/robots.txt")
      
      # Fetch and parse robots.txt
      rp = RobotFileParser()
      rp.set_url(robots_url)
      rp.read()
      
      # Check if the given URL is allowed
      return rp.can_fetch("*", url)
    
    except Exception as e:
      # Handle exceptions (e.g., network issues, invalid URL)
      print(f"Error checking robots.txt: {e}")
      return False


  def test_scrapegraphai(self, url):
    
    try:
      smart_scraper_graph = SmartScraperGraph(
          prompt="Estrai i titoli delle notizie e la lingua della notizia",
          source=url,
          config=self.graph_config,
      )

      result = smart_scraper_graph.run()
      
      return True

    except:
      return False

  def test_category(self, url):
    try:
      smart_scraper_graph = SmartScraperGraph(
          prompt="Estrai i titoli delle notizie, la lingua, e la categoria in base al titolo della notizia",
          source=url,
          config=self.graph_config,
      )


      result = smart_scraper_graph.run()

      news = result[list(result.keys())[0]]

      evaluation_result = 0
      total_news = len(news)
      user_input = None

      for el in news:
        for key in list(el.keys()):
          print(f"{key}: {el[key]}")
          print()
          user_input = input("1/2: True/False")
          if user_input == "1":
            evaluation_result += 1

      return evaluation_result / total_news
    
    except:
      return False


  def test_secondary_category(self, url):

    try:
      smart_scraper_graph = SmartScraperGraph(
          prompt="Estrai i titoli delle notizie, la lingua, la categoria della notizia in base al titolo e una categoria secondaria",
          source=url,
          config=self.graph_config,
      )


      result = smart_scraper_graph.run()

      news = result[list(result.keys())[0]]

      evaluation_result = 0
      total_news = len(news)
      user_input = None

      for el in news:
        for key in list(el.keys()):
          print(f"{key}: {el[key]}")
          print()
          user_input = input("1/2: True/False")
          if user_input == "1":
            evaluation_result += 1

      return evaluation_result / total_news
    
    except:
      return False


  def evaluate(self, scrape=True, scrapegraph=True, category=True, second_category=True):

    results = {
            "website": [],
            "url": [],
            "scrape": [],
            "scrapegraph": [],
            "categorization": [],
            "secondary_category": []}

    if self.links is None:
      print("Getting links...")
      self.get_links()
      print(f"{len(self.links)} links acquired")
      print()

    print("Cleaning website names...")
    self.clean_website_name()
    print("Website cleaned")


    print("Starting evaluation...")
    for i in range (len(self.links)):

      link = self.links.iloc[i]

      results["website"].append(link["website"])
      results["url"].append(link["url"])
      
      if scrape:
        results["scrape"].append(False if self.can_scrape(link["url"]) == False else True)
      else:
        results["scrape"].append(None)

      if scrapegraph:
        results["scrapegraph"].append(self.test_scrapegraphai(link["url"]))
      else:
        results["scrapegraph"].append(None)

      if category:
        results["categorization"].append(self.test_category(link["url"]))
      else:
        results["categorization"].append(None)
      
      if second_category:
        results["secondary_category"].append(self.test_secondary_category(link["url"]))
      else:
        results["secondary_category"].append(None)

    print("Evaluation finished")
    return pd.DataFrame(results)
