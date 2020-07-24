import datetime
import sys
import dateutil.parser
from business_rules.variables import (BaseVariables, numeric_rule_variable)

class VideoVariables(BaseVariables):
	def __init__(self, video):
		self.video = video

	@numeric_rule_variable()
	def likes(self):
		return len(self.video.get('likes', []))

	@numeric_rule_variable()
	def dislikes(self):
		return len(self.video.get('dislikes', []))

	@numeric_rule_variable()
	def comments(self):
		return len(self.video.get('comments', []))

	@numeric_rule_variable()
	def likeability(self):
		if self.likes() + self.dislikes() == 0:
			return 0
		return self.likes() / float(self.likes() + self.dislikes())

	@numeric_rule_variable()
	def days_since_publication(self):
		if 'upload_date' not in self.video:
			return sys.maxsize
		return (datetime.datetime.now() - dateutil.parser.parse(self.video['upload_date'])).days
