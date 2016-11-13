from flask import render_template, request, redirect
from app import app

import requests
import json
import datetime

from app.utils import format_price

from enum import Enum

# move this to a config file that will not be included in the repo
apiKey = app.config["API_KEY"] # get the API Key from the config file

# http://www.davidadamojr.com/handling-cors-requests-in-flask-restful-apis/
@app.after_request
def after_request(response):
	response.headers.add('Access-Control-Allow-Origin', '*')
	response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
	response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE')
	return response

# Home page route. Loads the accounts.
@app.route('/')
@app.route('/index')
def index():
	# create the URL for the request
	accountsUrl = 'http://api.reimaginebanking.com/accounts?key={}'.format(apiKey)
        merchantUrl = 'http://api.reimaginebanking.com/merchants?key={}'.format(apiKey)
	# make call to the Nessie Accounts endpoint
	accountsResponse = requests.get(accountsUrl)
	merchantResponse = requests.get(merchantUrl)
	
	# if the accounts call responds with success
	merchants = json.loads(merchantResponse.text)
	
	if accountsResponse.status_code == 200:
		accounts = json.loads(accountsResponse.text)


		# variable which will keep track of all purchases to pass to UI
		purchases = []
		
		
		for account in accounts:
			purchaseUrl = 'http://api.reimaginebanking.com/accounts/{}/purchases?key={}'.format(account['_id'], apiKey)
			purchaseResponse = requests.get(purchaseUrl)
			
			purchases.extend(json.loads(purchaseResponse.text))

		return render_template("home.html", accounts=accounts, format_price=format_price, purchases = purchases, merchants = merchants)
	else:
		return render_template("notfound.html")


@app.route('/transfer', methods=['POST'])
def postTransfer():
	
	fromAccount = request.form["fromAccount"]

	toAccount = request.form["toAccount"]

	amount = float(request.form["amount"]) # need to convert to an int or this fails

	description = request.form["description"]
	
	# set values that are not included in the form
	medium = "balance";
	dateObject = datetime.date.today()
	dateString = dateObject.strftime('%Y-%m-%d')

	# set up payload for request
	body = {
		
  "merchant_id": toAccount,
  "medium": "balance",
  "purchase_date": "2016-11-13",
  "amount": amount,
  "description": description

	}

	# make the request to create the payment
	url = "http://api.reimaginebanking.com/accounts/{}/purchases?key={}".format(fromAccount, apiKey)

	response = requests.post(
		url,
		data=json.dumps(body),
		headers={'content-type':'application/json'})
	
	# redirect user to the same page, which should now show there latest payment in the list
	return redirect("/index", code=302)
