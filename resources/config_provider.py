import configparser


def get_config_default():
    """
    Export content of config file as a dict
    :return: dict of configuration info
    """
    config = configparser.ConfigParser()
    config.read('resources/config.ini')
    return config['training']