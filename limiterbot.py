import praw
import time
import threading


now_time = time.time()


class limit_bot:
	# defined variables
	def __init__(self):
		self.sub = # enter name of subreddit
		self.id = # enter user ID
		self.secret = # enter user secret ID
		self.username = # enter user username
		self.password = # enter user password
		self.user_agent = 'LimiterBot/0.1 by Mandjevant'
		self.reddit = praw.Reddit(client_id = self.id, client_secret = self.secret, password = self.password, user_agent = self.user_agent, username = self.username)

		self.time_between_posts = 1800 # user can only post once every self.time_between_posts seconds
		self.removal_message = ('Your post was removed because you are posting too often. You can only post once every ' + str(int(self.time_between_posts/60)) + ' minutes.')
		self.removal_title = ('Posting too often')
		self.removal_type = ('public')

		self.limitdict = {}


	# takes submission ID to remove entry in limitdict
	def remove_from_dict(self, submission):
		self.limitdict.pop(str(submission.author))


	# takes submission ID to remove the submission
	def post_remove(self, submission):
		self.reddit.submission(submission).mod.remove()																						
		self.reddit.submission(submission).mod.send_removal_message(message = self.removal_message, title = self.removal_title, type = self.removal_type)	


	# takes submission ID to update limitdict if submission is not yet present
	def try_add_to_dict(self, submission):
		if str(submission.author) in self.limitdict.keys():
			if submission == self.limitdict[str(submission.author)][0]:
				pass
			else:
				self.post_remove(submission)
		else:
			self.limitdict.update({str(submission.author): [submission, submission.created_utc]})

		print(self.limitdict)


	# checks new page in subreddit, evaluates submissions
	def check_new(self):
		print('thread 1 running')	
		try: 												
			start_time = time.time()		

			while True:				
				for submission in self.reddit.subreddit(self.sub).new(limit=100): 
					if (time.time() - submission.created_utc) < self.time_between_posts + 60:
						self.try_add_to_dict(submission)
					else:
						continue

				time.sleep(60.0 - ((time.time() - start_time) % 60.0)) 	

		except KeyboardInterrupt:
			pass


	# checks if submission in limitdict has exceeded submission rate limit
	def review_dict(self):
		print('thread 2 running')
		try:
			start_time = time.time()

			while True:
				for key, value in self.limitdict.copy().items():
					submission_author = key
					submission = self.reddit.submission(id=value[0])
					time_posted = value[1]
					if (time.time() - time_posted) > self.time_between_posts:
						self.remove_from_dict(submission)
					else:
						continue

				time.sleep(60.0 - ((time.time() - start_time) % 60.0))
		
		except KeyboardInterrupt:
			pass


	# threading to execute functions in parallel
	def threading(self):
		a = threading.Thread(target=self.check_new, name='Thread-a', daemon=True)		
		b = threading.Thread(target=self.review_dict, name='Thread-b', daemon=True)		

		a.start()																		
		b.start()																		

		a.join()																		
		b.join()


if __name__ == '__main__':
	limit_bot().threading()

	print('Processing time:', time.time() - now_time)


