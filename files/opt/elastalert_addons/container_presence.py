from collections import deque
from functools import partial, reduce
from itertools import ifilter, takewhile
from operator import methodcaller

from elastalert.ruletypes import RuleType
from elastalert.util import lookup_es_key


class ContainerPresenceRule(RuleType):
    required_options = set(['timeframe', 'container_name', 'container_count_min'])

    def __init__(self, *args):
        super(ContainerPresenceRule, self).__init__(*args)
        self.timeframe = self.rules['timeframe']
        self.history_size = self.rules.get('history_size', 1000)
        self.container_count_min = self.rules['container_count_min']
        self.container_heartbeats = deque([], self.history_size)
        self.container_id_field = self.rules.get('container_id_field', 'container.id')
        self.container_name = self.rules['container_name']

    def add_data(self, data):
        self.container_heartbeats.extend(ifilter(self._has_container_name, data))

    def garbage_collect(self, timestamp):
        recent_heartbeats = compose(
            list,
            partial(
                takewhile,
                lambda heartbeat: timestamp - heartbeat.get('@timestamp') < self.timeframe,
            ),
            reversed,
        )(self.container_heartbeats)

        container_ids = compose(
            set,
            partial(
                map,
                partial(
                    lookup_es_key,
                    term = self.container_id_field,
                ),
            ),
        )(recent_heartbeats)

        if len(container_ids) < self.container_count_min:
            self.add_match({
                'container_count': len(container_ids),
                'container_count_min': self.container_count_min,
                'container_ids': list(container_ids),
                'container_id_field': self.container_id_field,
                'container_name': self.container_name,
                'recent_heartbeats': recent_heartbeats,
                'timeframe': self.timeframe.total_seconds(),
                '@timestamp': timestamp,
            })

    def get_match_str(self, match):
        return (
            'Less than {match[container_count_min]} unique container '
            'identifiers for "{match[container_name]}" found in the last '
            '{match[timeframe]} seconds:'
        ).format(match=match)

    def _has_container_name(self, entry):
        return self.container_name in entry.get('container', {}).get('names', [])


def compose(*funcs):
    return lambda x: reduce(lambda v, f: f(v), reversed(funcs), x)

def maybe(func):
    return lambda value: func(value) if value is not None else value
