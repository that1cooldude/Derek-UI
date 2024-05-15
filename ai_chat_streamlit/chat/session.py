import json
import os
from typing import List, Tuple
import uuid
import yaml
from ai_chat_streamlit.chat.model import create_model


class Session:
    def __init__(self, config_file=None, on_state_changed=lambda: None):
        if not config_file:
            config_file = os.getenv("CHAT_CONFIG_FILE", "config.yaml")
        self.on_state_changed = on_state_changed
        self.messages = []
        with open(config_file, "r") as f:
            config = yaml.safe_load(f)
        self.models_config = config["models"]
        self.default_model = config["default_model"]
        assert self.default_model in self.models
        self.history_folder = config["history_folder"]
        if not os.path.exists(self.history_folder):
            os.makedirs(self.history_folder)

        self.messages = []
        self.history_file = None
        self.model_instance = {}

    @property
    def current_model(self):
        return self.default_model

    @property
    def models(self):
        return list(self.models_config.keys())

    @property
    def is_new_session(self):
        return not self.history_file

    @property
    def current_history(self):
        return self.history_file

    @property
    def history_files(self) -> List[Tuple[str, float, str]]:
        files = os.listdir(self.history_folder)
        files = [f for f in files if f.endswith(".jsonl")]
        modified_times = [os.path.getmtime(
            os.path.join(self.history_folder, f)) for f in files]
        first_lines = []
        for f in files:
            with open(os.path.join(self.history_folder, f), "r") as f:
                first_lines.append(yaml.safe_load(f.readline())["content"])
        ret = list(zip(files, modified_times, first_lines))
        ret.sort(key=lambda x: x[1], reverse=True)
        return ret

    def chat_model(self, model_name):
        if model_name not in self.model_instance:
            model_config = self.models_config[model_name]
            model = create_model(model_name, model_config)
            self.model_instance[model_name] = model
        return self.model_instance[model_name]

    def save_history(self):
        if self.is_new_session:
            self.history_file = f"session-{uuid.uuid4().hex}.jsonl"
        with open(os.path.join(self.history_folder, self.history_file), "w") as f:
            for message in self.messages:
                f.write(json.dumps(message) + "\n")
        if not self.is_new_session:
            self.on_state_changed()

    def add_message(self, role, content):
        self.messages.append({"role": role, "content": content})

    def set_history_file(self, filename: str) -> None:
        if filename:
            if filename != self.history_file:
                self.history_file = filename
                self.messages = []
                with open(os.path.join(self.history_folder, self.history_file), "r") as f:
                    for line in f:
                        self.messages.append(yaml.safe_load(line))
                self.on_state_changed()
        else:
            self.messages = []
            self.history_file = None

    def set_model(self, model_name: str) -> None:
        if model_name != self.current_model:
            self.default_model = model_name
            self.on_state_changed()
