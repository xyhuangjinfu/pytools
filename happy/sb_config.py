import json
import os


class SBConfig:
    def __init__(self):
        config_file_path = os.path.split(os.path.realpath(__file__))[0] + '/sb_config.json'
        f = open(config_file_path)
        self.config = json.load(f)


if __name__ == '__main__':
    print(os.path.split(os.path.realpath(__file__))[0])
