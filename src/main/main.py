import time
import datetime
import re
import requests
from difflib import context_diff

from bs4 import BeautifulSoup
import boto3
from botocore.exceptions import ClientError

from utils import config_loader


LINKS_CACHE = {}
TEXT_CACHE = {}


def send_email_alert(config, page_url, text_diff, links_diff):
    email_config = config['email']
    subject = "Url Checker: Some links have changed!"
    charset = "UTF-8"
    body_text = (
        "Url Checker checkin-in!\r\n",
        f"Page has changed: {page_url}\r\n",
        "Text Diff:\r\n"
        f"{''.join(text_diff)}\r\n"
        "Links Diff:\r\n"
        f"{''.join(links_diff)}"
    )

    aws_session = boto3.session.Session(profile_name=email_config['aws_profile'])
    client = aws_session.client('ses', region_name="eu-west-1")

    try:
        response = client.send_email(
            Destination={
                'ToAddresses': [
                    email_config['email_recipient'],
                ],
            },
            Message={
                'Body': {
                    'Text': {
                        'Charset': charset,
                        'Data': body_text,
                    },
                },
                'Subject': {
                    'Charset': charset,
                    'Data': subject,
                },
            },
            Source=email_config['email_sender'],
        )
    # Display an error if something goes wrong.
    except ClientError as e:
        log_message(e.response['Error']['Message'])
    else:
        log_message("Links-alert email sent!")


def log_message(msg):
    print(f"{datetime.datetime.now():%Y-%m-%d %H:%M} - {msg}")


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


def check_url(config, page_url):
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
            send_email_alert(config, page_url, text_diff, links_diff)
        else:
            # log_message("No text or links have changed since last visit.")
            pass
    else:
        log_message(f"Error fetching URL: {page_url}")


def loop_through(config):
    for url in config['page_urls']:
        check_url(config, url)


def startup_msg(config):
    print(f"Link-checker: I'll be checking for new links at these URLs every {config['check_frequency_seconds']} seconds:")
    for page in config['page_urls']:
        print(page)


def main():
    config = config_loader.load_config("config.yaml")
    startup_msg(config)

    try:
        while True:
            loop_through(config)
            time.sleep(config['check_frequency_seconds'])
    except KeyboardInterrupt:
        log_message('Exiting!')


if __name__ == "__main__":
    main()
