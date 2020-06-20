# pylint: disable=W0622
# pylint: disable=W0613
# pylint: disable=C0103

from durable.lang import *

with ruleset('comments_test'):
	@when_all(m.comments == '2')
	def comment_is_two(c):
		logger.debug('All comments are 2s')


with ruleset('choice_of_sequences'):
	@when_any(all(c.first << m.comments == '2',
				  c.second << m.likes == '5'),
			  all(c.first << m.comments == '5',
				  c.second << m.likes == 2))
	def action_sequences(c):
		msg = 'Comentarios es 2 y likes es 5'
		logger.debug(msg)
		return msg

with ruleset('one_nesting'):
	@when_all(c.user << (m.user == 'diegote') & (m.videos_stats.quantity > 10))
	def action_nesting(c):
		msg = 'Use un nivel de nesting'
		logger.debug(msg)
		return msg

with ruleset('array_matching'):
	@when_all(m.videos.allItems(item.comments < 5))
	def rule_1(c):
		return '{0} matches rule 1'

	@when_all(m.videos.allItems((item.comments >= 5) & (item.comments < 10)))
	def rule_2(c):
		return '{0} matches rule 2'

	@when_all(m.videos.allItems((item.comments >= 10) & (item.comments < 25)))
	def rule_3(c):
		return '{0} matches rule 3'
