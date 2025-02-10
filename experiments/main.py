import json
from simulator import Simulator

with open('config.json', 'r') as file:
    config = json.load(file)

cosmos = Simulator(**config.get('init', {}))

if __name__ == '__main__':
    cosmos.run(**config.get('run', {}))
    cosmos.export(**config.get('path'), {})
