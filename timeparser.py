# Needed maven thing under build->extensions
# <extension>
#     <groupId>co.leantechniques</groupId>
#     <artifactId>maven-buildtime-extension</artifactId>
#     <version>2.0.2</version>
# </extension>

import logging
import re
from functools import reduce
from pprint import pprint
from typing import Dict, Tuple

module_regex = re.compile(r"^\[INFO\]\s([a-zA-Z_-]+)$")
stage_regex = re.compile(r"^\[INFO\]\s\s\s([a-zA-Z_-]+):([a-zA-Z_-]+)\s\(([a-zA-Z_-]+)\)?[^[]*\[([^\]]*)]$")

text = open(r"C:\Users\Ryan\tmp\timings.log").read()

lines = text.splitlines()
current_stages = []
modules = {}


def get_duration(time: str) -> float:
    return float(time[:-1])


for line in lines:
    if module_regex.match(line):
        match = module_regex.match(line)
        current_module_name = match.groups()[0]
        modules[current_module_name] = modules.get(current_module_name, {})
        current_stages = modules[current_module_name]['stages'] = []
    elif stage_regex.match(line):
        match = stage_regex.match(line)
        stage = {}
        stage['plugin'] = match.groups()[0]
        stage['lifecycle'] = match.groups()[1]
        stage['time'] = match.groups()[-1]
        if len(match.groups()) == 4:
            stage['execution'] = match.groups()[2]
        elif len(match.groups()) == 3:
            stage['execution'] = 'UNKNOWN'
        else:
            logging.debug("Unknown length of stage groups (%s: )", match, match.groups())

        current_stages.append(stage)

total_time = sum([get_duration(stage['time'])
                  for module in modules.values()
                  for stage in module['stages']])

print(f'Total duration: {total_time:.5}s ({total_time/60:.4}m {total_time%60:.3}s)')

for module_name, module in modules.items():
    module['time'] = sum([get_duration(stage['time']) for stage in module['stages']])

sorted_times_desc = sorted([(module_name, module_data['time']) for module_name, module_data in modules.items()],
                           key=lambda x: x[1], reverse=True)
print('Average time per module: %f' % (sum(map(lambda x: x['time'], modules.values())) / len(modules.values())))

# pprint(sorted_times_desc)
plugin_tuples = [(stage['plugin'], get_duration(stage['time']))
                 for module in modules.values()
                 for stage in module['stages']]


def reduce_plugin_tuples(acc: Dict, val: Tuple) -> Dict:
    acc[val[0]] = acc.get(val[0], 0) + val[1]
    return acc


plugin_times_desc = sorted(reduce(reduce_plugin_tuples, plugin_tuples, {}).items(), key=lambda x: x[1], reverse=True)

pprint(plugin_times_desc)


