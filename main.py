# -*- coding: utf-8 -*-
"""Telegram bot for monitoring chat members"""
from __future__ import print_function  # for pylint

from pathlib import Path

import json
import logging
import os
import sys
import time
import urllib

import requests

CONF_FILE = "./conf.json"
URL = "https://api.telegram.org/bot{}/"

logFormatter = logging.Formatter(
	"%(asctime)s [%(threadName)-12.12s] [%(levelname)-5.5s]  %(message)s")
rootLogger = logging.getLogger()
rootLogger.setLevel(logging.DEBUG)

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
	url = get_api_url(token) + \
		"sendMessage?text={}&chat_id={}".format(text, chat_id)
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
		if not "message" in update or "edited_message" in update:
			return
		message_element = update["message"] if "message" in update else update["edited_message"]
		chat = message_element["chat"]["id"]
		rootLogger.debug(json.dumps(update))
		if "left_chat_participant" in message_element:
			left_user = message_element["left_chat_participant"]["first_name"]
			update_last_leaver_in_file(left_user, chat)
			send_message(left_user + " has left from chat", chat, token)
		elif "text" in message_element:
			handle_message_text(message_element["text"], chat, token)


def handle_message_text(message_text, chat, token):
	"""Handle message text"""
	rootLogger.debug(message_text)
	if message_text.startswith("/"):
		handle_command(message_text, chat, token)


def help_message():
	"""Returns help message"""
	return """
		Commands:
		/start - standard command, not useful for anything atm
		/help - returns help message, you are reading it now
		/last - last user that left the chat
	"""


def update_last_leaver_in_file(left_user, chat):
	"""Saves new value to file"""
	data_path_str = "./data" + str(chat)
	create_dir_if_not_exists(data_path_str)
	path_str = data_path_str + "/last.txt"
	create_file_if_not_exists(path_str)
	new_value = open(path_str, 'w')
	new_value.write(left_user)
	new_value.close()

def last_user_who_left(chat):
	"""Returns last user who left the chat or default message"""
	data_path_str = "./data" + str(chat)
	create_dir_if_not_exists(data_path_str)
	path_str = data_path_str + "/last.txt"
	create_file_if_not_exists(path_str)
	last_goner_file = Path(path_str)
	# check if not empty
	if last_goner_file.stat().st_size > 0:
		file_handler = open(path_str, 'r')
		file_content = file_handler.readline()
		file_handler.close()
		return file_content
	return "Nobody has ever quited from here"


def handle_command(text, chat, token):
	"""Command handler"""
	command_output = "That command I do not know."
	if text.startswith("/start"):
		command_output = "I was born ready."
	elif text.startswith("/help"):
		command_output = help_message()
	elif text.startswith("/last"):
		command_output = last_user_who_left(chat)
	send_message(command_output, chat, token)


def get_last_update_id(updates):
	"""Latest update id from result"""
	update_ids = []
	for update in updates["result"]:
		update_ids.append(int(update["update_id"]))
	return max(update_ids)


def get_conf(conf_file):
	"""Reads configuration in json format from file"""
	json_conf = None
	conf_file_path = Path(conf_file)
	if not conf_file_path.exists or not conf_file_path.is_file():
		rootLogger.error("Conf file conf.json not found!")
		sys.exit(1)
	elif conf_file_path.stat().st_size == 0:
		rootLogger.error("Conf file conf.json is empty!")
		sys.exit(1)
	with open(conf_file, mode="r", encoding="utf8") as f:
		json_conf = json.load(f)
	return json_conf


def setup_file_logger():
	"""Ensures that log directory exists"""
	log_dir_path = "./log/"
	create_dir_if_not_exists(log_dir_path)
	file_handler = logging.FileHandler("{0}/{1}.log".format(log_dir_path, "app"))
	file_handler.setFormatter(logFormatter)
	rootLogger.addHandler(file_handler)


def create_dir_if_not_exists(path_str):
	"""create folder if it does not exists"""
	if not os.path.exists(path_str):
		os.makedirs(path_str)

def create_file_if_not_exists(path_str):
	"""Create file if it's not existing"""
	file_path = Path(path_str)
	# check if file exists
	if not file_path.exists() or not file_path.is_file():
		# creating empty file
		open(path_str, 'a').close()


def main():
	"""Main function"""
	setup_file_logger()
	rootLogger.info("Starting up")
	json_conf = get_conf(CONF_FILE)
	if not "token" in json_conf or len(json_conf["token"]) is 0:
		rootLogger.error("No token!")
		sys.exit(1)
	token = json_conf["token"]
	last_update_id = None
	while True:
		updates = get_updates(token, last_update_id)
		if "result" in updates and len(updates["result"]) > 0:
			handle_updates(updates, token)
			last_update_id = get_last_update_id(updates) + 1
		time.sleep(1)


if __name__ == '__main__':
	main()
