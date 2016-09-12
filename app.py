from flask import Flask, request
import requests
import facebook
import logging

# Set up global variables here 
FB_APP_ID = '1406443076050507'
FB_SECRET = 'e95edd248a0f1282357d2b5baa0bae55'
FB_VALIDATION_TOKEN = 'PtvFy6W4keqfssZ8SdAxEKvxVm6FAX'
FB_PAGE_TOKEN = 'EAATZCJwvx3ksBAEG1ZBDkUqrf238XpwWRd4o29pi6l2qyl0ODxuZBqSU9aok4l0xj7MOwdOK7Wn3vyupo0axoSavF1CMwLNZBRZBWVYfvLonm8chW8ZCGDY9hVU1laWpjGXniwlGVcugrpQyTrLzuBYZCni7aAlsGPnTFtBB0WpitxCZAyNNybgy'

app = Flask(__name__)
graph = facebook.GraphAPI(access_token=FB_PAGE_TOKEN, version='2.2')

@app.route('/webhook', methods=['GET', 'POST'])
def webhook():
    if request.method == 'GET':
        if request.args['hub.mode'] == 'subscribe' and request.args['hub.verify_token'] == FB_VALIDATION_TOKEN:
            app.logger.info('Validating the webhook')
            return str(request.args['hub.challenge'])
        else:
            app.logger.error('Failed validation. Make sure the validation tokens match.')
            abort(403, message='Validation Failed')
    else:
        app.logger.debug('Received a post request with body %s' % request.json)
        if request.json['object'] == 'page':
            for entry in request.json['entry']:
                for msg in entry['messaging']:
                    if msg.get('postback'):
                        app.logger.info('User %s has initiated a conversation'%msg['sender']['id'])
                        user_info = requests.get('https://graph.facebook.com/v2.6/%s'%msg['sender']['id'],
                                    params={'access_token': FB_PAGE_TOKEN}).json()
                        send_message = requests.post('https://graph.facebook.com/v2.6/me/messages', 
                                      params={'access_token': FB_PAGE_TOKEN},
                                      json={'recipient': {'id': msg['sender']['id']}, 'message': {'text': 'Hi %s, nice to meet you'% user_info['first_name']}})
                        app.logger.info('Sent message response %s'%send_message.text)

                    elif msg.get('message') and not msg['message'].get('is_echo'):
                        app.logger.info('Reveived a new message from %s with contents %s'%(msg['sender']['id'], msg['message']['text']))
                        user_info = requests.get('https://graph.facebook.com/v2.6/%s'%msg['sender']['id'],
                                    params={'access_token': FB_PAGE_TOKEN}).json()
                        send_message = requests.post('https://graph.facebook.com/v2.6/me/messages', 
                                      params={'access_token': FB_PAGE_TOKEN},
                                      json={'recipient': {'id': msg['sender']['id']}, 'message': {'text': 'Hi %s, nice to meet you'% user_info['first_name']}})
                        app.logger.info('Sent message response %s'%send_message.text)
        return 'Done'

if __name__ == '__main__':
    handler = logging.StreamHandler()
    jsonatter = logging.Formatter(
        '%(asctime)s %(levelname)-8s %(message)s')
    handler.setFormatter(jsonatter)
    handler.setLevel(logging.DEBUG)
    app.logger.addHandler(handler)
    app.logger.setLevel(logging.DEBUG)
    app.run('0.0.0.0', debug=True, 
            ssl_context=('/home/abhishekram/certificates/abhishekram.hopto.org/fullchain1.pem', 
                         '/home/abhishekram/certificates/abhishekram.hopto.org/privkey1.pem'))
