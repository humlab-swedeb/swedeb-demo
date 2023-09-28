import os
from swedeb_demo.main_page_shared_filter import do_render


if __name__ == "__main__":
    env_file: str = os.environ.get('SWEDEB_ENV_FILENAME', "/app/.env")
    debug: bool = os.environ.get('SWEDEB_DEBUG', "False") == "True"
    cwb_registry: str = os.environ.get('SWEDEB_CWB_REGISTRY', "/data/registry")
    cwb_database: str = os.environ.get('SWEDEB_CWB_DATABASE', "False")
    do_render(env_file, debug, cwb_registry, cwb_database)  # type: ignore
