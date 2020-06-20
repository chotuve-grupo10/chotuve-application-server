# pylint: disable=W0622
# pylint: disable=W0611
# pylint: disable=C0411

import pytest
import app_server.rules
from durable.lang import *
from durable.engine import *

def test_comment_is_two():
	comments = {'user': 'diegote@gmail.com',
				'algo': 'algo_mas',
				'comments': 2}

	assert post('comments_test', comments)

def test_comment_is_two_likes_are_five():
	data_first = {'comments': 2}
	data_second = {'likes': 5}

	post('choice_of_sequences', data_first)
	assert post('choice_of_sequences', data_second)

def test_comment_is_two_likes_are_not_five():
	data_first = {'comments': 2}
	data_second = {'likes': 3}

	post('choice_of_sequences', data_first)
	with pytest.raises(MessageNotHandledException):
		post('choice_of_sequences', data_second)

def test_comment_is_five_likes_are_two():
	data_first = {'comments': 5}
	data_second = {'likes': 2}

	post('choice_of_sequences', data_first)
	assert post('choice_of_sequences', data_second)

def test_one_nesting():
	data = {'user': 'diegote',
			'videos_stats': {'total_duration_hrs': 150,
							 'quantity': 25}
			}

	assert post('one_nesting', data)

def test_one_nesting_fails():
	data = {'user': 'diegote',
			'videos_stats': {'total_duration_hrs': 150,
							 'quantity': 5}
			}

	with pytest.raises(MessageNotHandledException):
		post('one_nesting', data)

def test_array_behaviour():
	data_1 = {'user': 'user01',
			  'videos': [{'id': 0, 'comments': 2},
						 {'id': 1, 'comments': 4},
						 {'id': 2, 'comments': 2}]}

 	# resp == 'user01 matches rule 1'
	assert post('array_matching', data_1)
