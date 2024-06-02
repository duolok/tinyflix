import yaml

class Config:
    def __init__(self, conf_file='config.yaml'):
        with open(conf_file, 'r') as f:
            config = yaml.safe_load(f)
        self.movie_table = config['movie_table']
        self.movie_bucket = config['movie_bucket']

config = Config()
