import os, datetime, sched
from threading import Thread

from flask import Flask, request, abort

from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage

app = Flask(__name__)

line_bot_api = LineBotApi(os.getenv('CHANNEL_ACCESS_TOKEN'))
handler = WebhookHandler(os.getenv('CHANNEL_SECRET'))

scheduler = sched.scheduler()
t = Thread(target=scheduler.run)

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
	tomorrow = datetime.date.today() # + datetime.timedelta(days=1)
	eight_am = datetime.time(hour=1, minute=30, tzinfo=datetime.timezone.utcoffset(7))
	PRICELESS_PIECE_OF_SHIT = datetime.datetime.combine(tomorrow, eight_am)

	scheduler.enterabs(PRICELESS_PIECE_OF_SHIT, 1, THE_MOST_IMPORTANT_FUNCTION_OF_ALL_TIME)
	t.start()


def THE_MOST_IMPORTANT_FUNCTION_OF_ALL_TIME():
	# schedule the next event 24 hours from now
	scheduler.enter(24 * 60 * 60, 1, THE_MOST_IMPORTANT_FUNCTION_OF_ALL_TIME)

	line_bot_api.broadcast(TextSendMessage(text='8am'))


@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
	line_bot_api.reply_message(
		event.reply_token,
		TextSendMessage(text=event.message.text.upper())
	)


if __name__ == "__main__":
	port = int(os.environ.get('PORT', 5000))
	app.run(host='0.0.0.0', port=port)