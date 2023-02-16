import logging
import os

import functions_framework
import requests
from bs4 import BeautifulSoup
from google.cloud import storage
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

logging.basicConfig(level=logging.INFO)

def save_string_to_gcs_bucket(bucket_name, file_name, string_to_save):
    """Saves a string as a text file to a Google Cloud Storage bucket."""

    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(file_name)

    # Convert the string to bytes before saving to the bucket
    string_bytes = string_to_save.encode('utf-8')

    # Save the string to the bucket
    blob.upload_from_string(string_bytes, content_type='text/plain')


def read_string_from_gcs_bucket(bucket_name, file_name):
    """Reads a string from a text file in a Google Cloud Storage bucket."""

    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(file_name)

    # Download the file contents as bytes
    file_bytes = blob.download_as_bytes()

    # Convert the bytes to a string
    file_string = file_bytes.decode('utf-8')

    return file_string

def parse_message(content):
    """Take the content of a message page, and return the title and body"""
    soup = BeautifulSoup(content, 'html.parser')
    
    message_title = soup.find_all("td",{"class":"Boards-MessageTitle"})[1].text
    message_body = soup.find_all("td",{"class":"Boards-Message"})[0].text
    
    return message_title, message_body


def pull_message(index):
    """"Query a given message ID, and return the content if it exists"""
    url = f"https://secure.marathonguide.com/Forums/CherryBlossomTenMile.cfm?step=4&MID={index}&Topic=175" # noqa

    r = requests.get(url)

    if "invalid URL" in r.text:
        # message doesn't exist
        return
    else:
        return r.content


def send_email(subject, body, index):

    message = Mail(
        from_email='jack.welty@gmail.com',
        to_emails='jack.welty@gmail.com',
        subject='New 10 miler forum post',
        html_content=f"""<strong>There is a new forum post in the Cherry Blossom 10
            miler forum.</strong><p>The subject of the post is: {subject}</p>
            <p>The body of the post is: {body}</p>
            <p> Access the message <a href="https://secure.marathonguide.com/Forums/CherryBlossomTenMile.cfm?step=4&MID={index}&Topic=175">here</a>.</p>
            """ # noqa
            )
    
    try:
        sg = SendGridAPIClient(os.environ.get('SENDGRID_API_KEY'))
        response = sg.send(message)
        print(response.status_code)
        print(response.body)
        print(response.headers)
        return 'Email sent successfully!'
    except Exception as e:
        print(str(e))
        return 'Email could not be sent.'


@functions_framework.http
def check_messages(request):

    # Pull the index of the most recent pulled message
    index = int(read_string_from_gcs_bucket('bib-search','latest_index.txt'))

    logging.info(f'Latest index: {index}')
    index += 1
    logging.info(f'Trying the message at index: {index}')

    # Try and grab the index +1 message
    next_message = pull_message(index)

    while next_message:
        message_title, message_body = parse_message(next_message)

        logging.info(f'New message: {message_title}\n{message_body}')

        # Send me a notification email
        send_email(message_title, message_body, index)

        # store latest index
        index += 1

        # Look for the next (next) message
        next_message = pull_message(index)

    else:
        logging.info("No more messages, storing index and quitting.")
        index -= 1
        logging.info(f'Searching done, storing last pulled index: {index}')
        save_string_to_gcs_bucket('bib-search','latest_index.txt',str(index))
        logging.info('Index stored!')
        return 'OK'

if __name__ == '__main__':
    check_messages()