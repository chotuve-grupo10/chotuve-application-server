from business_rules.actions import BaseActions, rule_action
from business_rules.fields import FIELD_NUMERIC

class VideoActions(BaseActions):
	def __init__(self, video, variables):
		self.video = video
		self.variables = variables

	@rule_action(params={"penalty": FIELD_NUMERIC})
	def penalize(self, penalty):
		self.__set_importance(lambda importance: importance - penalty)

	@rule_action(params={"bonus": FIELD_NUMERIC})
	def boost(self, bonus):
		self.__set_importance(lambda importance: importance + bonus)

	@rule_action(params={"factor": FIELD_NUMERIC})
	def multiply_likes(self, factor):
		self.__multiply(self.variables.likes(), factor)

	@rule_action(params={"factor": FIELD_NUMERIC})
	def multiply_comments(self, factor):
		self.__multiply(self.variables.comments(), factor)

	def __multiply(self, variable, factor):
		self.__set_importance(lambda importance: importance + variable * factor)

	def __set_importance(self, importance_function):
		importance = self.video.get('importance', 0)
		importance = importance_function(importance)
		self.video['importance'] = importance
