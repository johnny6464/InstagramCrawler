import requests
import configparser

config = configparser.ConfigParser()
config.read('config.ini')

HEADER = {
	'user-agent'     : 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Mobile Safari/537.36',
	'cookie'         : config['COOKIES']['COOKIE'],
	'accept-encoding': 'gzip, deflate, sdch, br',
	'accept-language': 'zh-CN,zh;q=0.8',
	'accept'         : '*/*'
}

def get_html(url):
	try:
		response = requests.get(url, headers=HEADER)
		return response.text
	except:
		print("請求html錯誤，錯誤狀態碼: ", response.status_code)
		return None


def get_json(url):
	try:
		response = requests.get(url, headers=HEADER, timeout=10)
		return response.json()
	except:
		print("請求json錯誤，錯誤狀態碼: ", response.status_code)
		return get_json(url)


def get_content(url):
	try:
		response = requests.get(url, headers=HEADER, timeout=10)
		return response.content
	except:
		print("請求圖片url錯誤，錯誤狀態碼: ", response.status_code)
		return None