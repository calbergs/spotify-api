import yaml

def yaml_loader():
    """Reads in a config.yaml file"""
    config = yaml.safe_load(open('/opt/airflow/operators/config.yml'))
    return config