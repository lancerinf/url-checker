import yaml
import os


def load_config(config_path):
    with open(config_path, "rb") as file_stream:
        return yaml.safe_load(file_stream)


def main():
    config = load_config(os.path.join(os.path.dirname(__file__), '../resources/config/config.yaml'))
    print(config)


if __name__ == "__main__":
    main()
