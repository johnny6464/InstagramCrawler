import collections
import configparser
import datetime
import json
import os
import pickle
import random
import re
import shutil
import time
from hashlib import md5

from pyquery import PyQuery as pq

from database import DBManager
from packet import get_content, get_html, get_json

URL_BASE = "https://www.instagram.com/"
URL_POSTER = URL_BASE + "graphql/query/?query_hash=e769aa130647d2354c40ea6a439bfc08&variables=%7B%22id%22%3A%22{user_id}%22%2C%22first%22%3A12%2C%22after%22%3A%22{cursor}%22%7D"
URL_SHORTCODE = URL_BASE + "graphql/query/?query_hash=109cdd03d7468e12222ad164fbea3ca3&variables=%7B%22shortcode%22%3A%22{shortcode}%22%7D"
URL_INFO = URL_BASE + "graphql/query/?query_hash=c9100bf9110dd6361671f113dd02e7d6&variables=%7B%22user_id%22%3A%22{user_id}%22%2C%22include_chaining%22%3Atrue%2C%22include_reel%22%3Atrue%2C%22include_suggested_users%22%3Afalse%2C%22include_logged_out_extras%22%3Afalse%2C%22include_highlight_reels%22%3Atrue%2C%22include_related_profiles%22%3Afalse%7D"
URL_FOLLOWER = URL_BASE + "graphql/query/?query_hash=c76146de99bb02f6415203be841dd25a&variables=%7B%22id%22%3A%22{user_id}%22%2C%22include_reel%22%3Atrue%2C%22fetch_mutual%22%3Atrue%2C%22first%22%3A12%2C%22after%22%3A%22{cursor}%22%7D"
URL_REEL = URL_BASE + "graphql/query/?query_hash=52a36e788a02a3c612742ed5146f1676&variables=%7B%22reel_ids%22%3A%5B%22{user_id}%22%5D%2C%22tag_names%22%3A%5B%5D%2C%22location_ids%22%3A%5B%5D%2C%22highlight_reel_ids%22%3A%5B%5D%2C%22precomposed_overlay%22%3Afalse%2C%22show_story_viewer_list%22%3Atrue%2C%22story_viewer_fetch_count%22%3A50%2C%22story_viewer_cursor%22%3A%22%22%2C%22stories_video_dash_manifest%22%3Afalse%7D"


Poster = collections.namedtuple('Image', ["image", "time", "likes"])

class Manager():
	def __init__(self, id):
		self.id = id
		self.save_path = f"{os.path.abspath('.')}\\data\\{id}"
		self.config = configparser.ConfigParser()
		self.config.read('config.ini')
		self.db = DBManager(self.config)
		self.user_id = re.findall('"profilePage_([0-9]+)"', get_html(f"{URL_BASE}{self.id}/"), re.S)[0]


	def checkSavePath(self):
		if not os.path.exists(self.save_path):
			os.makedirs(self.save_path)


	def get_poster(self):
		shortcodes = self.get_shortcode()
		imgs = self.get_img(shortcodes)

		if len(imgs) == 0:
			print("沒有新照片囉QQ")
			return
		else:
			print(f"共取得{len(imgs)}張照片,開始下載~~~")

		self.download(imgs[::-1], f"{self.save_path}\\photo")
		print("貼文下載完成")


	def get_reel(self):
		reel_urls = []
		url = URL_REEL.format(user_id=self.user_id)
		js_data = get_json(url)

		try:
			items = js_data['data']['reels_media'][0]['items']
		except:
			print("當前沒有動態喔~~")
			return

		for item in items:
			if item['is_video']:
				reel_urls.append(item['video_resources'][0]['src'])
			else:
				reel_urls.append(item['display_url'])
		today = datetime.date.today()
		print(f"共取得{len(reel_urls)}個限時動態,開始下載~~~")
		self.download(reel_urls, f"{self.save_path}\\reel\\{today.month}-{today.day}")
		print("動態下載完成")


	def get_follower(self):
		followers = []
		cursor = ""
		flag = True

		print("查詢中...")
		while flag:
			url = URL_FOLLOWER.format(user_id=self.user_id, cursor=cursor)
			js_data = get_json(url)
			edges = js_data['data']['user']['edge_followed_by']['edges']
			page_info = js_data['data']['user']['edge_followed_by']['page_info']
			cursor = page_info['end_cursor']
			flag = page_info['has_next_page']
			for edge in edges:
				followers.append(edge['node']['username'])

		print(f"當前有{len(followers)}個追蹤者")

		if os.path.exists(f'{self.save_path}\\follower.pkl'):
			with open(f'{self.save_path}\\follower.pkl', 'rb') as file:
				pre_followers = pickle.load(file)
				difference = set(followers).symmetric_difference(set(pre_followers))
				if len(difference) != 0:
					if len(difference.intersection(set(followers))) != 0:
						print(f"{difference.intersection(set(followers))}新追蹤")
					if len(difference.intersection(set(pre_followers))) != 0:
						print(f"{difference.intersection(set(pre_followers))}已退追")
				else:
					print("追蹤人數沒有變化")

		with open(f'{self.save_path}\\follower.pkl', 'wb') as file:
			pickle.dump(followers, file)


	def get_shortcode(self):
		shortcodes = []
		pre_ts = self.db.query(self.id)

		html = get_html(f"{URL_BASE}{self.id}/")
		doc = pq(html)
		items = doc('script[type="text/javascript"]').items()

		#前12張shortcode
		for item in items:
			if item.text().strip().startswith('window._sharedData'):
				js_data = json.loads(item.text()[21:-1], encoding='utf-8')
				edges = js_data['entry_data']['ProfilePage'][0]['graphql']['user']['edge_owner_to_timeline_media']['edges']
				if len(edges) == 0:
					return []
				page_info = js_data['entry_data']['ProfilePage'][0]['graphql']['user']['edge_owner_to_timeline_media']['page_info']
				cursor = page_info['end_cursor']
				flag = page_info['has_next_page']
				ts = edges[0]['node']['taken_at_timestamp']
				for edge in edges:
					if int(pre_ts) >= int(edge['node']['taken_at_timestamp']):
						self.db.update(self.id, ts)
						return shortcodes
					shortcodes.append(edge['node']['shortcode'])
		#後續圖片shortcode
		while flag:
			url = URL_POSTER.format(user_id=self.user_id, cursor=cursor)
			js_data = get_json(url)
			edges = js_data['data']['user']['edge_owner_to_timeline_media']['edges']
			cursor = js_data['data']['user']['edge_owner_to_timeline_media']['page_info']['end_cursor']
			flag = js_data['data']['user']['edge_owner_to_timeline_media']['page_info']['has_next_page']
			for edge in edges:
				if int(pre_ts) >= int(edge['node']['taken_at_timestamp']):
					self.db.update(self.id, ts)
					return shortcodes
				shortcodes.append(edge['node']['shortcode'])
			print(f"已取得{len(shortcodes)}個shortcode")
		self.db.update(self.id, ts)
		return shortcodes


	def get_img(self, shortcodes):
		urls = []
		count = 0

		print("開始取得網址")
		#依照shortcode查url
		for shortcode in shortcodes:
			count = count + 1
			url = URL_SHORTCODE.format(shortcode=shortcode)
			js_data = get_json(url)

			try:
				if 'edge_sidecar_to_children' in js_data['data']['shortcode_media']:
					edges = js_data['data']['shortcode_media']['edge_sidecar_to_children']['edges']
					for edge in edges:
						if edge['node']['is_video']:
							video_url = edge['node']['video_url']
							if video_url:
								urls.append(video_url)
						else:
							if edge['node']['display_url']:
								display_url = edge['node']['display_url']
								urls.append(display_url)
				else:
					if js_data['data']['shortcode_media']['is_video']:
						video_url = js_data['data']['shortcode_media']['video_url']
						urls.append(video_url)
					else:
						display_url = js_data['data']['shortcode_media']['display_url']
						urls.append(display_url)
				print(f"已取得{len(urls)}個照片網址")
				time.sleep(2 + float(random.randint(1, 800))/200)
			except:
				print(f"第{count}則貼文異常")
		return urls


	def download(self, imgs, path):
		if not os.path.exists(path):
			os.makedirs(path)

		for index in range(len(imgs)):
			try:
				content = get_content(imgs[index])
				f_ext = imgs[index].find("?")
				img_name = f"{path}\\{md5(content).hexdigest()}.{imgs[index][f_ext-3:f_ext]}"
				if not os.path.exists(img_name):
					with open(img_name, 'wb') as file:
						file.write(content)
						file.flush()
					file.close()
			except Exception as e:
				print(e)


	def clear_data(self):
		self.db.delete(self.id)
		if os.path.exists(self.save_path):
			shutil.rmtree(self.save_path)
