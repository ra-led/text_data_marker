import yaml


def load_yaml_config(filename):
    return yaml.load(
        stream=open(filename, encoding="utf8"),
        Loader=yaml.SafeLoader
        )


CFG = load_yaml_config("conf.yml")
