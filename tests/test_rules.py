import datetime
import pytest
from app_server import rules

def test_base_importance():
	rule_list = []
	video = {}
	rules.set_importance(video, rule_list)
	assert 'importance' in video
	assert video['importance'] == 0

def test_set_likes_importance():
	rule_likes = [
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
		}
	]
	video = {
						'likes': ['diegote', 'guillote', 'eche']
					}
	rules.set_importance(video, rule_likes)
	assert 'importance' in video
	assert video['importance'] == pytest.approx(0.6)

def test_set_comments_importance():
	rule_comments = [
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
		}
	]
	video = {
						'likes': ['diegote', 'guillote', 'eche'],
						'dislikes': ['cosso', 'gonza'],
						'comments': [
							{'user': 'nico', 'comment': 'buen vidio', 'timestamp': 'now'},
							{'user': 'cosso', 'comment': 'No me gusta', 'timestamp': 'yesterday'},
						]
					}
	rules.set_importance(video, rule_comments)
	assert 'importance' in video
	assert video['importance'] == pytest.approx(0.8)

def test_set_likes_dislikes_ratio_importance():
	rule_likes_dislikes_ratio = [
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
		}
	]
	video = {
						'likes': ['diegote', 'guillote', 'eche'],
						'dislikes': ['cosso', 'gonza', 'agus', 'maxi'],
						'comments': [
							{'user': 'nico', 'comment': 'buen vidio', 'timestamp': 'now'},
							{'user': 'cosso', 'comment': 'No me gusta', 'timestamp': 'yesterday'},
						]
					}
	rules.set_importance(video, rule_likes_dislikes_ratio)
	assert 'importance' in video
	assert video['importance'] == pytest.approx(-2)

def test_set_last_videos_importance():
	rule_last_week = [
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
	new_video = {'upload_date': datetime.datetime.now()}
	old_video = {'upload_date': datetime.datetime.now() - datetime.timedelta(days=10)}
	rules.set_importance(new_video, rule_last_week)
	rules.set_importance(old_video, rule_last_week)
	assert 'importance' in new_video
	assert 'importance' in old_video
	assert new_video['importance'] == pytest.approx(5)
	assert old_video['importance'] == 0
