import yaml

def yaml_loader():
    """Reads in a config.yaml file"""
    config = yaml.safe_load(open('/opt/airflow/plugins/config.yaml'))
    return config