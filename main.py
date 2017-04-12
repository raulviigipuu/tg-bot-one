# -*- coding: utf-8 -*-
"""Telegram bot for monitoring chat members"""
from __future__ import print_function  # for pylint

import json
import logging
import sys
import time
import urllib

import requests

CONF_FILE = "conf.json"
URL = "https://api.telegram.org/bot{}/"

logFormatter = logging.Formatter("%(asctime)s [%(threadName)-12.12s] [%(levelname)-5.5s]  %(message)s")
rootLogger = logging.getLogger()
rootLogger.setLevel(logging.INFO)

fileHandler = logging.FileHandler("{0}/{1}.log".format("./log/", "app"))
fileHandler.setFormatter(logFormatter)
rootLogger.addHandler(fileHandler)

consoleHandler = logging.StreamHandler()
consoleHandler.setFormatter(logFormatter)
rootLogger.addHandler(consoleHandler)

def get_api_url(token):
	"""Returns URL for tg api"""
	return URL.format(token)

def get_url(url):
	"""Returns url content"""
	response = requests.get(url)
	content = response.content.decode("utf8")
	return content


def send_message(text, chat_id, token):
	"""Send message to chat"""
	text = urllib.parse.quote_plus(text)
	rootLogger.info("MESSAGE TEXT: " + text)
	url = get_api_url(token) + "sendMessage?text={}&chat_id={}".format(text, chat_id)
	get_url(url)


def get_json_from_url(url):
	"""Returns url content as json object"""
	content = get_url(url)
	json_content = json.loads(content)
	return json_content


def get_updates(token, offset=None):
	"""Returns updates considered not seen"""
	url = get_api_url(token) + "getUpdates?timeout=100"
	rootLogger.debug(url)
	if offset:
		url += "&offset={}".format(offset)
	json_content = get_json_from_url(url)
	return json_content


def handle_updates(updates, token):
	"""Handle updates from Telegram"""
	rootLogger.debug("Handling updates")
	for update in updates["result"]:
		chat = update["message"]["chat"]["id"]
		rootLogger.debug(json.dumps(update))
		if "left_chat_participant" in update["message"]:
			left_user = update["message"]["left_chat_participant"]["first_name"]
			send_message(left_user + " has left from chat", chat, token)


def get_last_update_id(updates):
	"""Latest update id from result"""
	update_ids = []
	for update in updates["result"]:
		update_ids.append(int(update["update_id"]))
	return max(update_ids)


def get_conf(conf_file_path):
	"""Reads configuration in json format from file"""
	json_conf = None
	with open(conf_file_path, mode="r", encoding="utf8") as conf_file:
		json_conf = json.load(conf_file)
	return json_conf


def main():
	"""Main function"""
	rootLogger.info("Starting up")
	json_conf = get_conf(CONF_FILE)
	if not "token" in json_conf or len(json_conf["token"]) is 0:
		rootLogger.error("No token!")
		sys.exit(1)
	token = json_conf["token"]
	last_update_id = None
	while True:
		updates = get_updates(token, last_update_id)
		if len(updates["result"]) > 0:
			handle_updates(updates, token)
			last_update_id = get_last_update_id(updates) + 1
		time.sleep(1)


if __name__ == '__main__':
	main()
