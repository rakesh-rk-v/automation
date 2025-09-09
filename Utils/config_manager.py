# Utils/config_manager.py
from Utils.yaml_reader import YamlReader


class ConfigManager:
    _instance = None
    _app = None

    @classmethod
    def initialize(cls, env, app):
        if cls._instance is None:
            cls._instance = YamlReader(env,app)
        cls._app = app

    @classmethod
    def get_config(cls):
        if cls._instance is None:
            raise Exception("ConfigManager not initialized.")
        return cls._instance

    @classmethod
    def get_schema(cls,app=None):
        if app==None:
            return cls._instance.get_schema_value(cls._app)
        else:
            return cls._instance.get_schema_value(app)
