# eight.am
### wake up refreshed every morning with `eight.am`

Head over to [LINE](line.me) and add `eight.am` as a friend. 

---

This service is hosted on [Heroku](heroku.com). To make a local instance or push more changes:
1. clone this repo and run `heroku login`
2. activate virtual environment with `. venv/bin/activate`
3. `pip install -r requirements.txt`
4. grab the required environment variables
5. `heroku ps:scale web=1`
6. `heroku local` or `git push heroku master`
