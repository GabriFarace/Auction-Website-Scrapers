# 🛠️ Machinery & Equipment Taxonomy Scrapers

This repository contains a collection of Python scripts designed to extract machinery and equipment taxonomies and prices from various websites.
The project uses Selenium, BeautifulSoup, and Requests to scrape structured and unstructured data from sources with different levels of complexity.

## 📌 Overview

Different websites expose their taxonomies in different formats — some dynamically rendered using JavaScript, others delivered as static HTML.
This repository provides a unified scraping toolkit capable of handling:

- JavaScript-heavy pages (via Selenium)

- Static HTML content (via Requests + BeautifulSoup)

- Hybrid or paginated sources

- Sites with anti-scraping patterns (user-agents, delays, retries)

The output of each scraper is processed, cleaned, and exported as JSON, CSV, or any format required by downstream systems.
