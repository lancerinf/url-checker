import time
import datetime
import re
import requests
from difflib import context_diff

from bs4 import BeautifulSoup
import boto3
from botocore.exceptions import ClientError

CHECK_FREQUENCY_SECONDS = 300  # 5 minutes
PAGE_URLS = ["https://your-path.com"]
EMAIL_THROUGH_AWS_PROFILE = "your-aws-profile" # aws-profile
EMAIL_SENDER = "Url Checker <sender-address>" # an AWS SES validated email
EMAIL_RECIPIENT = "recipient-address" # a valid recipient for your AWS SES

LINKS_CACHE = {}
TEXT_CACHE = {}


def send_email_alert(page_url, text_diff, links_diff):
    sender = EMAIL_SENDER
    recipient = EMAIL_RECIPIENT
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

    aws_session = boto3.session.Session(profile_name=EMAIL_THROUGH_AWS_PROFILE)
    client = aws_session.client('ses', region_name="eu-west-1")

    try:
        response = client.send_email(
            Destination={
                'ToAddresses': [
                    recipient,
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
            Source=sender,
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


def check_url(page_url):
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
            send_email_alert(page_url, text_diff, links_diff)
        else:
            # log_message("No text or links have changed since last visit.")
            pass
    else:
        log_message(f"Error fetching URL: {page_url}")


def loop_through(page_urls):
    for url in page_urls:
        check_url(url)


def startup_msg():
    print(f"Link-checker: I'll be checking for new links at these URLs every {CHECK_FREQUENCY_SECONDS} seconds:")
    for page in PAGE_URLS:
        print(page)


def main():
    startup_msg()

    try:
        while True:
            loop_through(PAGE_URLS)
            time.sleep(CHECK_FREQUENCY_SECONDS)
    except KeyboardInterrupt:
        log_message('Exiting!')


if __name__ == "__main__":
    main()
