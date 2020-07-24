from business_rules.variables import (BaseVariables,
																			numeric_rule_variable,
																			string_rule_variable)
import datetime
import math

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
		return self.likes() / float(self.likes() + self.dislikes())

	@numeric_rule_variable()
	def days_since_publication(self):
		if 'upload_date' not in self.video:
			return math.inf
		return (datetime.datetime.now() - self.video['upload_date']).days
				