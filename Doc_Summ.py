import re
import nltk
import textract as txt
import requests as req
import heapq as hp
from bs4 import BeautifulSoup as Bs
import boto3
import requests
import json
import os

AWS_ACCESS_KEY_ID = "ASIAWTUSJPUFX6D2MGM2"
AWS_SECRET_ACCESS_KEY = "cwzYSoL+CocywSf8wU4Sp/0MdN2UQKYsXPcbDW8W"
AWS_SESSION_TOKEN = "FwoGZXIvYXdzEO///////////wEaDAy/Zdi4iTor61SFoyLAAdp2x87eEiukmddoSLnXL4cRBzAYAlq1bGQxdSwM+Z8TQpVlMPLThxE8/BFx1y7xUeDQypgomi36+J90mCo220ixd+GTwKiFe0cDdmTLORf63PvAYvc2zeqPMNFBhzy36IvhizxuJXEpI9N9zLpdJSfDXbbkxPwdv0zgzsQJFI0oDeg1TmoYqpT2reF+CfDwcH6QKqckFwQbxkDlhBGVPR7fGvm5kVLSipUZ/qC+KoN3nZuFdPzz4ukV25zOuDWS0yj2ytyhBjItoBCtzyV0t0vSYTqGqF7iVDoUxWoXPdEo6Tau3YbxTkxyeC0An4QW89TfhhXP"
AWS_REGION_NAME = "us-east-1"

s3 = boto3.client('s3', aws_access_key_id=AWS_ACCESS_KEY_ID,
                      aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
                      aws_session_token=AWS_SESSION_TOKEN,
                      region_name=AWS_REGION_NAME)

sqs = boto3.client('sqs', aws_access_key_id=AWS_ACCESS_KEY_ID,
                      aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
                      aws_session_token=AWS_SESSION_TOKEN,
                      region_name=AWS_REGION_NAME)

comprehend = boto3.client('comprehend', aws_access_key_id=AWS_ACCESS_KEY_ID,
                      aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
                      aws_session_token=AWS_SESSION_TOKEN,
                      region_name=AWS_REGION_NAME)

sqs_queue_url="https://sqs.us-east-1.amazonaws.com/454499597579/Broker"

class Doc_Summ:

    scraped_content = ''
    refined_text_content = ''
    sentence_token = ''
    word_token = ''
    frequency_dict = {}
    sentence_score = {}

    def __init__(self):
        self.scraped_content=''
        self.refined_text_content=''
        self.sentence_score=''
        self.word_token=''
        self.frequency_dict={}
        self.sentence_score={}

    def txt_sum(self):
        self.scraped_content = ''
        obj = s3.get_object(Bucket='inputtext', Key='test.txt')
        self.scraped_content = obj['Body'].read().decode('utf-8')
        self.text_cleaning()

    def web_scraping(self, string):
        sqs_message = {
            'url': string
        } 
        sqs.send_message(
            QueueUrl=sqs_queue_url,
            MessageBody=json.dumps(sqs_message)
        )
        self.scraped_content = json.loads(requests.post(os.environ.get('API_GATEWAY_URL')).text)['message']   
        self.text_cleaning()

    # “Remove all traces of emoji from a text file.,” Gist. [Online]. Available: https://gist.github.com/slowkow/7a7f61f495e3dbb7e3d767f97bd7304b. [Accessed: 01-Apr-2023]. 
    def text_cleaning(self):
        self.refined_text_content = re.sub(r'\[.*?\]', ' ', self.scraped_content)  # Remove all the contents from square braces
        self.refined_text_content = re.sub(r'[_!#$%^*?/\|~:]', ' ', self.refined_text_content)  # Remove all the special characters
        self.refined_text_content = re.sub(r'\([^()]*\)', ' ', self.refined_text_content)  # Remove all the contents from parentheses
        self.refined_text_content = re.sub(r'\{[^{}]*\}', ' ', self.refined_text_content)  # Remove all the contents from curly braces
        self.refined_text_content = re.sub(r'\<[^<>]*\>', ' ', self.refined_text_content)  # Remove all the contents from angular braces
        self.refined_text_content = re.sub(r'\s+\/\s+', ' ', self.refined_text_content)  # Remove urls
        self.refined_text_content = re.sub(r'@\s+', ' ', self.refined_text_content)  # Remove mentions
        self.refined_text_content = re.sub(r'#\s+', ' ', self.refined_text_content)  # Remove trends
        self.refined_text_content = re.sub(r'['
                                  u'\U0001F600-\U0001F64F'  
                                  u'\U0001F300-\U0001F5FF'  
                                  u'\U0001F680-\U0001F6FF'  
                                  u'\U0001F1E0-\U0001F1FF'  
                                  ']+', ' ', self.refined_text_content)  # Remove emojis and symbols
        self.refined_text_content = re.sub(r'\n', ' ', self.refined_text_content)
        self.refined_text_content = re.sub(r'\t', ' ', self.refined_text_content)
        self.refined_text_content = re.sub(r'\s+', ' ', self.refined_text_content)  

        self.sentence_token = self.refined_text_content
        self.sentence_token = nltk.sent_tokenize(self.sentence_token)  

        self.refined_text_content = re.sub(r'[^a-zA-Z]', ' ', self.refined_text_content)  
        self.refined_text_content = re.sub(r'\s+', ' ', self.refined_text_content) 

        self.word_token = self.refined_text_content
        self.word_token = nltk.word_tokenize(self.word_token) 
        self.stopwords()

    def stopwords(self):
        stopwords = nltk.corpus.stopwords.words('english')
        for word in self.word_token:
            if word not in stopwords:
                if word not in self.frequency_dict.keys():
                    self.frequency_dict[word] = 1
                else:
                    self.frequency_dict[word] += 1

        max_word_freq = max(self.frequency_dict.values())

        for word in self.frequency_dict.keys():
            self.frequency_dict[word] /= max_word_freq
        self.score_sentence()

    def score_sentence(self):
        
        for sent in self.sentence_token:  
            for word in nltk.word_tokenize(sent.lower()):  
                if word in self.frequency_dict.keys():  
                    if len(sent.split(' ')) < 30:  
                        if sent not in self.sentence_score.keys():  
                            self.sentence_score[sent] = self.frequency_dict[word]
                        else:  
                            self.sentence_score[sent] += self.frequency_dict[word]

    def create_summary(self, n):
        summary = hp.nlargest(n, self.sentence_score)
        return summary