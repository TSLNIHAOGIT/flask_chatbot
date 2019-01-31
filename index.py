from flask import Flask, request, jsonify, render_template
import os
import dialogflow
import requests
import json
import pusher
from flask import Flask
from flask import jsonify
from flask import request
import requests
import json
import pandas as pd
df_huashu=pd.read_excel('huashu0.xlsx')

json_name='chatbot-example-new.json'#'cryptoassistant-be67b-38e847ce6c0c.json'
with open(json_name) as f:
    auth=json.load(f)
    print(auth)

import os
os.environ["GOOGLE_APPLICATION_CREDENTIALS"]=json_name

app = Flask(__name__)


# initialize Pusher
# pusher_client = pusher.Pusher(
#     app_id=os.getenv('PUSHER_APP_ID'),
#     key=os.getenv('PUSHER_KEY'),
#     secret=os.getenv('PUSHER_SECRET'),
#     cluster=os.getenv('PUSHER_CLUSTER'),
#     ssl=True)


@app.route('/')
def index():
    return render_template('index.html')


profile_new = {'fullName': '王强', 'principal': '1,000', 'loanBeginDate': "2018年1月3日", 'paymentDueDay': '2018年3月3日',
                   'apr': '5%', 'penalty': '200', 'debtCompanyName': '平安E贷', 'collectCompanyName': '江苏逸能',
                   'customerID': '123', 'gender': '先生',
                   'collector': '小张', 'balance': '1250', 'informDeadline': '后天下午3点',
                   'splitDebtMaxTolerance': '一个月', 'splitDebtFirstPay': '800', 'deltaTime': ' ', 'interestDue': '50',
                   'delinquencyDays': '30', 'cutDebtPay': '1000'}

@app.route('/get_response', methods=['GET', 'POST'])
def get_response():

    #服务器端获取客户端的请求（post/get），以及传递过滤的json参数
    json_from_client = request.get_json(silent=True, force=True,)
    print('myjson',json_from_client)
    name=json_from_client["queryResult"]["intent"]['displayName']
    print('name',name)
    # success_response = df_huashu[df_huashu['label'] == name]['message_finish'].sample(1).values[0]

    def file_process(input_str):
        # print('input_str',input_str,type(input_str))
        input_str = input_str.format(**profile_new)
        # print('input_str_new',input_str)
        return input_str

    success_response=df_huashu[df_huashu['label'] == name]['message'].apply(lambda row: file_process(row))
    success_response=success_response.sample(1).values[0]

    print('success_response',success_response)



    dic = {'fulfillmentText':success_response} #服务器端没有返回时，dialogflow才会用静态的rensponse
    return jsonify(dic) #返回给客户端显示的数据

# @app.route('/get_movie_detail', methods=['POST'])
# def get_movie_detail():
#     data = request.get_json(silent=True)
#
#     try:
#         movie = data['queryResult']['parameters']['movie']
#         api_key = os.getenv('OMDB_API_KEY')
#
#         movie_detail = requests.get('http://www.omdbapi.com/?t={0}&apikey={1}'.format(movie, api_key)).content
#         movie_detail = json.loads(movie_detail)
#
#         response =  """
#             Title : {0}
#             Released: {1}
#             Actors: {2}
#             Plot: {3}
#         """.format(movie_detail['Title'], movie_detail['Released'], movie_detail['Actors'], movie_detail['Plot'])
#     except:
#         response = "Could not get movie detail at the moment, please try again"
#
#     reply = {
#         "fulfillmentText": response,
#     }
#
#     return jsonify(reply)

# def detect_intent_texts(project_id, session_id, text, language_code):
#     session_client = dialogflow.SessionsClient()
#     session = session_client.session_path(project_id, session_id)
#
#     if text:
#         text_input = dialogflow.types.TextInput(
#             text=text, language_code=language_code)
#         query_input = dialogflow.types.QueryInput(text=text_input)
#         response = session_client.detect_intent(
#             session=session, query_input=query_input)
#
#         return response.query_result.fulfillment_text


def detect_intent_texts(project_id, session_id, text, language_code):
    """Returns the result of detect intent with texts as inputs.

    Using the same `session_id` between requests allows continuation
    of the conversation."""

    import dialogflow_v2 as dialogflow
    session_client = dialogflow.SessionsClient()

    session = session_client.session_path(project_id, session_id)
    print('Session path: {}\n'.format(session))
    text_input = dialogflow.types.TextInput(
        text=text, language_code=language_code)

    query_input = dialogflow.types.QueryInput(text=text_input)

    response = session_client.detect_intent(
        session=session, query_input=query_input)
    return response.query_result.fulfillment_text




@app.route('/send_message', methods=['POST'])
def send_message():
    # socketId = request.form['socketId']
    message = request.form['message']
    project_id =auth["project_id"]# os.getenv('DIALOGFLOW_PROJECT_ID')

    fulfillment_text = detect_intent_texts(project_id, "unique", message, 'en')
    response_text = { "message":  fulfillment_text }
    

    # pusher_client.trigger('movie_bot', 'new_message',
    #                     {'human_message': message, 'bot_message': fulfillment_text})
                        
    return jsonify(response_text)

# run Flask app
if __name__ == "__main__":
    app.run()