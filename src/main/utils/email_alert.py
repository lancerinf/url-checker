import boto3
from botocore.exceptions import ClientError

import logging


def send_email_through_aws_ses(email_config, diff_message):
    subject = "Url Checker: Some links have changed!"
    charset = "UTF-8"
    body_text = diff_message

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
        logging.error(e.response['Error']['Message'])
    else:
        logging.info("Url Checker: Alert email sent!")
