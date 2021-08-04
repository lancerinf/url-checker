import os
import time
import re
import requests

from bs4 import BeautifulSoup
from difflib import context_diff

from utils.config_loader import load_config
from utils.logging import log_message
from utils.ses_email import send_email_alert

LINKS_CACHE = {}
TEXT_CACHE = {}


def cache_and_diff(cache, key, new_value):
    diff = []
    if key in cache:
        reference = cache[key]
        diff = list(context_diff(reference, new_value, lineterm='\r\n'))
    cache[key] = new_value
    return diff


def clean_from_js(soup):
    [tag.decompose() for tag in soup.find_all('script')]
    [tag.find_parent().decompose() for tag in soup.find_all(string=re.compile("You need JavaScript enabled to view it"))]


def check_url(page_url, email_config):
    response = requests.request("GET", page_url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')

        article_body = soup.find(itemprop='articleBody')
        clean_from_js(article_body)

        # this is how BeautifulSoup extracts the part of webpage that you want to monitor for changes in text.
        text_of_interest = [str(line) for line in article_body.find_all('p')]
        text_diff = cache_and_diff(TEXT_CACHE, page_url, text_of_interest)

        # this is how BeautifulSoup extracts the part of webpage that you want to monitor for new links.
        links_in_text_of_interest = [str(link) for link in article_body.find_all('a')]
        links_diff = cache_and_diff(LINKS_CACHE, page_url, links_in_text_of_interest)

        if text_diff or text_diff:
            log_message(f"Some text or links have changed! Check: {page_url}")
            if email_config['alert_enabled'] is True:
                send_email_alert(email_config, page_url, text_diff, links_diff)
    else:
        log_message(f"Error fetching URL: {page_url}")


def loop_through(url_checker_config, email_config):
    for url in url_checker_config['page_urls']:
        check_url(url, email_config)


def startup_msg(url_checker_config):
    log_message('Url Checker: Starting up!')
    log_message(f"Checking for new links at these URLs every {url_checker_config['check_frequency_seconds']} seconds:")
    for page in url_checker_config['page_urls']:
        log_message(page)


def main():
    config = load_config(os.path.join(os.path.dirname(__file__), 'resources/config/config.yaml'))
    url_checker_config = config['url_checker']
    email_config = config['email']

    startup_msg(url_checker_config)

    try:
        while True:
            loop_through(url_checker_config, email_config)
            time.sleep(url_checker_config['check_frequency_seconds'])
    except KeyboardInterrupt:
        log_message('Exiting!')


if __name__ == "__main__":
    main()
