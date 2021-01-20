import tkinter as tk
from manager import Manager
from timer import Timer

class Application(tk.Frame):
	def __init__(self, master=None):
		super().__init__(master)
		self.master = master
		self.pack()
		self.create_widgets()


	def create_widgets(self):
		self.lbl_header = tk.Label(self, text="Instagram Crawler")
		self.lbl_header.pack()

		self.query_frame = tk.Frame(self)
		self.query_frame.pack(side=tk.TOP)
		self.lbl_query = tk.Label(self.query_frame, text="請輸入欲查詢的帳號:")
		self.lbl_query.pack(side=tk.LEFT)
		self.txt_id = tk.Entry(self.query_frame)
		self.txt_id.pack(side=tk.LEFT)
		self.txt_id.focus_set()
		self.btn_query = tk.Button(self.query_frame, text="查詢", command=self.query)
		self.btn_query.pack(side=tk.BOTTOM)

		self.select_frame = tk.Frame(self)
		self.select_frame.pack(side=tk.TOP)
		self.btn_poster = tk.Button(self.select_frame, text="貼文", state="disabled", command=lambda: self.controller(0))
		self.btn_poster.pack(side=tk.LEFT)
		self.btn_reel = tk.Button(self.select_frame, text="限時", state="disabled", command=lambda: self.controller(1))
		self.btn_reel.pack(side=tk.LEFT)
		self.btn_follower = tk.Button(self.select_frame, text="追蹤", state="disabled", command=lambda: self.controller(2))
		self.btn_follower.pack(side=tk.LEFT)
		self.btn_clear = tk.Button(self.select_frame, text="清空", state="disabled", command=lambda: self.controller(3))
		self.btn_clear.pack(side=tk.LEFT)

		self.quit = tk.Button(self, text="QUIT", fg="red", command=self.master.destroy)
		self.quit.pack(side=tk.BOTTOM)


	def query(self):
		try:
			self.admin = Manager(self.txt_id.get())
			print(f"查詢 {self.admin.id} 成功")
			self.btn_poster['state'] = 'normal'
			self.btn_reel['state'] = 'normal'
			self.btn_follower['state'] = 'normal'
			self.btn_clear['state'] = 'normal'
		except:
			print(f"ID: {self.txt_id.get()}不存在")


	def controller(self, command):
		self.admin.checkSavePath()

		t = Timer()

		if command == 0:
			self.admin.get_poster()
		elif command == 1:
			self.admin.get_reel()
		elif command == 2:
			self.admin.get_follower()
		elif command == 3:
			self.admin.clear_data()

		t.span()
		print("Complete~~~~~\n")


if __name__ == '__main__':
	app = Application(master=tk.Tk())
	app.mainloop()