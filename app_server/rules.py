from business_rules import run_all
from app_server.video_variables import VideoVariables
from app_server.video_actions import VideoActions

def set_importance(video, rules):
	video['importance'] = 0
	variables = VideoVariables(video)
	actions = VideoActions(video, variables)
	run_all(rule_list=rules,
					defined_variables=variables,
					defined_actions=actions,
					stop_on_first_trigger=False
					)