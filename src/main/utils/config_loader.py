import yaml


def load_config(config_path):
    with open(config_path, "rb") as file_stream:
        return yaml.safe_load(file_stream)


def main():
    config = load_config("../config.yaml")
    print(config)


if __name__ == "__main__":
    main()
