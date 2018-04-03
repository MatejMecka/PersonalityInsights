import praw
from praw.exceptions import APIException
from prawcore.exceptions import NotFound
import prawcore
import requests
from requests.auth import HTTPBasicAuth
import time
from config import *
import sys
import os
import json

r = praw.Reddit(user_agent=userAgent,
					 client_id=clientID, client_secret=clientSecret,
					 username=user, password=passw)



def getUserComments(dude):
	print('Comments for User: {} '.format(r.redditor(dude)))
	with open('userscommentsreddit.txt', 'w+', encoding='utf8') as file:
		for comment in r.redditor(dude).comments.new(limit=None):
			print('{}'.format(comment.body))
			file.write('{}'.format(comment.body))
	data = open('userscommentsreddit.txt', 'rb').read()
	headers = {'Content-Type': 'text/plain;charset=utf-8','Accept':'application/json'}
	res = requests.post(watsonUrl, auth=(usernameWatson,passwordWatson), data=data, headers=headers)
	print(json.loads(res.text))
	jsondata = json.loads(res.text)
	if res.status_code == 200:
		trust = jsondata["personality"][3]["children"][5]["percentile"] * 100
		coop = jsondata["personality"][3]["children"][1]["percentile"] * 100
		agree = jsondata["personality"][3]["percentile"] * 100
		symp = jsondata["personality"][3]["children"][4]["percentile"] * 100
		response = {'trust':round(trust),'cooperation': round(coop),'agreeablness':round(agree), 'sympathy': round(symp)}
		return response
	elif res.status_code == 429:
		return "ratelimit"
	else:
		return "user<100"	

"""
* Get Each Persons comment
* If it Starts with the required command then take the username and call getUserComments
* If Not Found reply that it couldn't be found
"""

def main():
	while True:
		try:
			for mention in r.inbox.mentions(limit=50):
				if mention.new:
					mention.mark_read()
					print('{} - {} '.format(mention.author,mention.body))
					if mention.body.startswith(trigger):
						person = mention.body.split()[1]
						if person.startswith('/u/'):
							person = person[3:]
						try: 
							r.redditor(person).fullname
							res = getUserComments(person)
							if res == "user<100":
								mention.reply('User has less than 100 Words. Cannot Verify Trust Worth levels! If you thi \n\n  _This was performed by a bot using the IBM Watson API(Personality insights api). For any information about the bot pm /u/matejmecka. This bot is in beta._')
							elif res == 'ratelimit':
								mention.reply("Oopsie Woopsie. \n\n I've been Ratelimited by IBM. Please Try Again Later \n\n\ _This was performed by a bot using the IBM Watson API(Personality insights api). For any information about the bot pm /u/matejmecka. This bot is in beta._")
							else:	
								mention.reply('User can be trusted {}% based on his Reddit History\n\n You can also consider this information about the following person: \n\n He/She is {}% Cooperate \n\n They can be {}% Agreeable \n\n and can be {}% Sympathetic \n\n ***** \n _This was performed by a bot using the IBM Watson API(Personality insights api). For any information about the bot pm /u/matejmecka. This bot is in beta._'.format(str(res['trust']), str(res['cooperation']), str(res['agreeablness']), str(res['sympathy'])))
						except NotFound:
							mention.reply('Person not found! \n\n ***** _This was performed by a bot using the IBM Watson API(Personality insights api). For any information about the bot pm /u/matejmecka. This Bot is in beta._')
				else:
					pass
			time.sleep(5)
		except APIException as e:
			print(str(e))
			break
			sys.exit(1)


if __name__ == '__main__':
	main()