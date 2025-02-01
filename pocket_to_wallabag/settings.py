from pydantic_settings import BaseSettings, SettingsConfigDict


class ImporterSettings(BaseSettings):
    pocket_url = "https://getpocket.com/v3"
    pocket_consumer_key = "CHANGE-ME"
    redirect_uri = "about:blank"

    wallabag_username = "CHANGEME"
    wallabag_url = "https://CHANGE.ME"
    wallabag_client_id = "CHANGE_ME"
    wallabag_client_secret = "CHANGE_ME"
    wallabag_username = "CHANGEME"
    wallabag_password = "CHANGE_ME"

    model_config = SettingsConfigDict(env_prefix="importer_")
