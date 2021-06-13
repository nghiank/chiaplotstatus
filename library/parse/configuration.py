import pathlib
import os
import yaml

from library.utilities.exceptions import InvalidYAMLConfigException


def _get_config():
    directory = pathlib.Path().resolve()
    file_name = 'config.yaml'
    file_path = os.path.join(directory, file_name)
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Unable to find the config.yaml file. Expected location: {file_path}")
    f = open(file_path, 'r')
    config = yaml.load(stream=f, Loader=yaml.Loader)
    f.close()
    return config

def get_config_info():
    config = _get_config()    
    return config
