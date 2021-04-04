"""Read the latest Real Python tutorials
Usage:
------
    $ flowi [options] [id] [id ...]
List the latest tutorials:
    $ realpython
Read one tutorial:
    $ realpython <id>
    where <id> is the number shown when listing tutorials.
Read the latest tutorial:
    $ realpython 0
Available options are:
    -h, --help         Show this help
    -l, --show-links   Show links in text
0
"""
# Standard library imports
import argparse
import json

from flow_chart.flow_chart import FlowChart

if __name__ == '__main__':
    train_parser = argparse.ArgumentParser(description='Training arguments')

    # Add the arguments
    print('hey from train!!')
    train_parser.add_argument('--chart', type=json.loads, help='flow chart')
    args = train_parser.parse_args()
    flow_chart_json = args.chart

    print(flow_chart_json)
    print(type(flow_chart_json))

    flow_chart = FlowChart(flow_chart_json=flow_chart_json)
    flow_chart.run()
