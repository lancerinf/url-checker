import time
import datetime
import requests
from difflib import context_diff

from bs4 import BeautifulSoup
import boto3
from botocore.exceptions import ClientError

CHECK_FREQUENCY_SECONDS = 300  # 5 minutes
PAGE_URLS = ["https://<your-path>.com"]
EMAIL_THROUGH_AWS_PROFILE = "<your-profile>" # aws-profile
EMAIL_SENDER = "Url Checker <sender-address>" # an AWS SES validated email
EMAIL_RECIPIENT = "<recipient-address>" # a valid recipient for your AWS SES

LINKS_CACHE = {}


def startup_msg():
    print(f"Link-checker: I'll be checking for new links at these URLs every {CHECK_FREQUENCY_SECONDS} seconds:")
    for page in PAGE_URLS:
        print(page)


def log_message(msg):
    print(f"{datetime.datetime.now():%Y-%m-%d %H:%M} - {msg}")


def loop_through(page_urls):
    for url in page_urls:
        check_url(url)


def check_url(page_url):
    response = requests.request("GET", page_url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        links_in_text_of_interest = [str(link) for link in soup.find(itemprop='articleBody').find_all('a')] # here is how beautifulsoup extracts the part of webpage that you want to monitor for new links.
        if page_url in LINKS_CACHE:
            reference = LINKS_CACHE[page_url]
            diff_result = list(context_diff(reference, links_in_text_of_interest))
            if diff_result:
                log_message(f"Some links have changed! Check: {page_url}")
                send_email_alert(page_url, diff_result)
            else:
                log_message("Links haven't changed since last visit.")
        else:
            LINKS_CACHE[page_url] = links_in_text_of_interest
            log_message(f"First links scraping done for: {page_url}")
        pass
    else:
        log_message(f"Error fetching URL: {page_url}")


def send_email_alert(page_url, diff):
    sender = EMAIL_SENDER
    recipient = EMAIL_RECIPIENT
    subject = "Url Checker: Some links have changed!"
    body_text = ("Url Checker checkin-in!\r\n"
                 "\r\n"
                 f"Links have changed in: {page_url}\r\n"
                 "\r\n"
                 "Diff:\r\n"
                 f"{diff}\r\n"
                 )
    charset = "UTF-8"

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


def main():
    startup_msg()

    while True:
        loop_through(PAGE_URLS)
        time.sleep(CHECK_FREQUENCY_SECONDS)


if __name__ == "__main__":
    main()
