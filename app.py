import os, sched, requests
from datetime import datetime, date, time, timedelta
from dateutil import tz
from threading import Thread

from flask import Flask, request, abort

from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, FollowEvent, TextMessage, TextSendMessage, VideoSendMessage

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


def get_recipient_id(source):
	if source.type == 'user':
		return source.user_id
	elif source.type == 'group':
		return source.group_id
	elif source.type == 'room':
		return source.room_id


def search_gif(query, random_id):
	"""
	Returns a dictionary of GIFs according to https://developers.giphy.com/docs/api/schema/#gif-object
	"""

	res = requests.get('https://api.giphy.com/v1/gifs/random?api_key=' + \
		os.getenv('GIPHY_API_KEY') + \
		'&tag=' + \
		query + \
		'&random_id=' + \
		random_id
	)

	return = res.json()['data']['images']


def send_gif(recipient, query):
	gif = search_gif(query, recipient)

	print(gif['original']['mp4'])
	print(gif['480w_still']['url'])

	line_bot_api.push_message(
		recipient,
		VideoSendMessage(
			original_content_url=gif['original']['mp4'],
    		preview_image_url=gif['480w_still']['url']
		)
	)


@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
	to = get_recipient_id(event.source)

	line_bot_api.push_message(to, TextSendMessage(text='8 am'))
	line_bot_api.push_message(to, TextSendMessage(text=event.message.text.upper()))
	send_gif(to, '8 am')

@handler.default()
def default(event):
	to = get_recipient_id(event.source)

	line_bot_api.push_message(to, TextSendMessage(text='WAKEY WAKEY!'))	
	line_bot_api.push_message(to, TextSendMessage(text='IT\'S 8 AM!!'))


if __name__ == "__main__":
	port = int(os.environ.get('PORT', 5000))
	app.run(host='0.0.0.0', port=port)