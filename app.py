import os, sched, requests
from datetime import datetime, date, time, timedelta
from dateutil import tz
from threading import Thread

from flask import Flask, request, abort

from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage, VideoSendMessage

app = Flask(__name__)

line_bot_api = LineBotApi(os.getenv('CHANNEL_ACCESS_TOKEN'))
handler = WebhookHandler(os.getenv('CHANNEL_SECRET'))

scheduler = sched.scheduler()
t = Thread(target=scheduler.run)
t.start()

@app.route("/callback", methods=['POST'])
def callback():
	# get X-Line-Signature header value
	signature = request.headers['X-Line-Signature']

	# get request body as text
	body = request.get_data(as_text=True)
	app.logger.info("Request body: " + body)

	# handle webhook body
	try:
		schedule_broadcast()
		handler.handle(body, signature)
	except InvalidSignatureError:
		print("Invalid signature. Please check your channel access token/channel secret.")
		abort(400)

	t.join()
	return 'OK'


def schedule_broadcast():
	tomorrow = date.today() # + timedelta(days=1)
	eight_am = time(hour=18, minute=30)#, tzinfo=tz.gettz("Asia/Bangkok"))
	starting_time = datetime.combine(tomorrow, eight_am).timestamp()

	scheduler.enterabs((datetime.now() + timedelta(minutes=1)).timestamp(), 1, broadcast)


def broadcast():
	# schedule the next event 24 hours from now
	scheduler.enter(3, 1, broadcast)

	line_bot_api.broadcast(TextSendMessage(text='8am'))


def search_gif(query):
	res = requests.get('api.giphy.com/v1/gifs/random?api_key=' + \
		os.getenv('GIPHY_API_KEY') + \
		'&tag=' + \
		query
	)
	vid_url = res['data']['images']

	return vid_url


def send_gif(token, query):
	gif = search_gif(query)

	line_bot_api.reply_message(
		token,
		VideoSendMessage(
			original_content_url=gif['original']['mp4'],
    		preview_image_url=gif['480w_still']['url']
		)
	)


@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
	line_bot_api.broadcast(TextSendMessage(text='8am'))
	line_bot_api.reply_message(
		event.reply_token,
		TextSendMessage(text=event.message.text.upper())
	)
	send_gif(event.reply_token, '8 am')


if __name__ == "__main__":
	port = int(os.environ.get('PORT', 5000))
	app.run(host='0.0.0.0', port=port)