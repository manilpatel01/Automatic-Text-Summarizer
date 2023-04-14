from flask import Flask, render_template, jsonify, make_response, request
import textract as txt
from Doc_Summ import Doc_Summ
import os
import boto3

app = Flask(__name__)
app.config["TEMPLATES_AUTO_RELOAD"] = True

AWS_ACCESS_KEY_ID = "ASIAWTUSJPUFX6D2MGM2"
AWS_SECRET_ACCESS_KEY = "cwzYSoL+CocywSf8wU4Sp/0MdN2UQKYsXPcbDW8W"
AWS_SESSION_TOKEN = "FwoGZXIvYXdzEO///////////wEaDAy/Zdi4iTor61SFoyLAAdp2x87eEiukmddoSLnXL4cRBzAYAlq1bGQxdSwM+Z8TQpVlMPLThxE8/BFx1y7xUeDQypgomi36+J90mCo220ixd+GTwKiFe0cDdmTLORf63PvAYvc2zeqPMNFBhzy36IvhizxuJXEpI9N9zLpdJSfDXbbkxPwdv0zgzsQJFI0oDeg1TmoYqpT2reF+CfDwcH6QKqckFwQbxkDlhBGVPR7fGvm5kVLSipUZ/qC+KoN3nZuFdPzz4ukV25zOuDWS0yj2ytyhBjItoBCtzyV0t0vSYTqGqF7iVDoUxWoXPdEo6Tau3YbxTkxyeC0An4QW89TfhhXP"
AWS_REGION_NAME = "us-east-1"

s3 = boto3.client('s3', aws_access_key_id=AWS_ACCESS_KEY_ID,
                      aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
                      aws_session_token=AWS_SESSION_TOKEN,
                      region_name=AWS_REGION_NAME)


@app.route('/')
def home():
    response = s3.get_object(Bucket='frontendhtml', Key='index.html')
    html = response['Body'].read().decode('utf-8')
    return html

@app.route('/test', methods=["POST"])
def webscrapping():
    url = request.form['url']
    no_of_lines = int(request.form['lines'])
    doc = Doc_Summ()
    doc.web_scraping(url)
    l1 = doc.create_summary(no_of_lines)
    print(l1)
    return jsonify(l1)

@app.route('/test1', methods=["POST"])
def textinput():
    input_text = request.form['text']
    no_of_lines = int(request.form['lines'])
    s3.put_object(Bucket='inputtext', Key='test.txt', Body=input_text.encode())
    doc = Doc_Summ()
    doc.txt_sum()
    l1 = doc.create_summary(no_of_lines)
    return jsonify(l1)


if __name__ == "__main__":
    app.run(debug=True)