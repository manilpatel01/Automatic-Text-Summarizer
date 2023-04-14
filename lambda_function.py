import json
import boto3
import requests
from bs4 import BeautifulSoup
import os 


sqs = boto3.client('sqs')


def lambda_handler(event, context):
    
    scraped_content=''
    
    url = os.environ.get('Sqs_URL')
    
    response = sqs.receive_message(
        QueueUrl=url,
        MaxNumberOfMessages=1,
    ).get('Messages')
    
    message = response[0]
    message_body = json.loads(message['Body'])
    
    sqs.delete_message(
        QueueUrl=url,
        ReceiptHandle=message['ReceiptHandle']
    )

    html_doc = requests.get(message_body['url']) 
    soup = BeautifulSoup(html_doc.content, 'html.parser')
    acc_ele = ['a', 'abbr', 'acronym', 'b', 'big',
               'blockquote', 'br', 'center', 'cite', 'code', 'dd',
               'dfn', 'dir', 'div', 'dl', 'dt', 'em',
               'font', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'i',
               'ins', 'kbd', 'label', 'legend', 'li', 'ol',
               'p', 'pre', 'q', 'samp', 'small', 'span',
               'strong', 'sub', 'sup', 'tt', 'u', 'ul', 'var', 'head', 'header', 'body', 'article', 'section']
    para_contents = soup.findAll('p') 
    for tag in soup.findAll(True):  
        if tag.name not in acc_ele:
            tag.extract()  
    
    for contents in para_contents:
        scraped_content += contents.text  
    return { 
        'message' : scraped_content
    }
