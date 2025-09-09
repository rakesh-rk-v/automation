# Utils/yaml_reader.py
import yaml
import os

class YamlReader:
    def __init__(self, env,app):
        self.env = env
        self.app= app

        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) # Gets directory of yaml_reader.py
        file_path = os.path.join(project_root, "DataFiles", "Common", "config.yaml")

        # file_path ="C://Users//KNOT//PycharmProjects//PyTestOne//DataFiles//Common//config.yaml"
        # os.path.join(os.getcwd(), "config.yaml")
        with open(file_path, "r") as f:
            self.data = yaml.safe_load(f)

        if self.env not in self.data:
            raise KeyError(f"Environment '{self.env}' not found in YAML file.")

    def get_value(self, key):
        return self.data[self.env].get(key)

    def get_schema_value(self, app_key):
        try:
            return self.data[self.env]["schema"][app_key]
        except KeyError:
            raise KeyError(f"App '{app_key}' not found under 'schema' in env '{self.env}'")
