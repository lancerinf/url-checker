import boto3
from botocore.exceptions import ClientError

from .logging import log_message


def send_email_alert(email_config, page_url, text_diff, links_diff):
    subject = "Url Checker: Some links have changed!"
    charset = "UTF-8"
    body_text = (f"""
        Url Checker checkin-in!\r\n
        Page has changed: {page_url}\r\n
        Text Diff:\r\n
        {''.join(text_diff)}\r\n
        Links Diff:\r\n
        {''.join(links_diff)}\r\n""")

    aws_session = boto3.session.Session(profile_name=email_config['aws_profile'])
    client = aws_session.client('ses', region_name="eu-west-1")

    try:
        client.send_email(
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
        log_message("Url Checker: Alert email sent!")
