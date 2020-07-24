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

ruleset = [
	{
		'conditions': {
			'all': [
				{
					'name': 'likes',
					'operator': 'greater_than',
					'value': 0,
				}
			]
		},
		'actions': [
			{
				'name': 'multiply_likes',
				'params': {'factor': 0.2}
			}
		]
	},
	{
		'conditions': {
			'all': [
				{
					'name': 'comments',
					'operator': 'greater_than',
					'value': 0,
				}
			]
		},
		'actions': [
			{
				'name': 'multiply_comments',
				'params': {'factor': 0.4}
			}
		]
	},
	{
		'conditions': {
			'all': [
				{
					'name': 'likeability',
					'operator': 'less_than',
					'value': 0.5,
				}
			]
		},
		'actions': [
			{
				'name': 'penalize',
				'params': {'penalty': 2}
			}
		]
	},
	{
		'conditions': {
			'all': [
				{
					'name': 'days_since_publication',
					'operator': 'less_than',
					'value': 7,
				}
			]
		},
		'actions': [
			{
				'name': 'boost',
				'params': {'bonus': 5}
			}
		]
	}
]
