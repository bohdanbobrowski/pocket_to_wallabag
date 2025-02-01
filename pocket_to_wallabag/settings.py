from pydantic_settings import BaseSettings, SettingsConfigDict


class ImporterSettings(BaseSettings):
    pocket_consumer_key: str = ""
    pocket_url: str = ""
    redirect_uri: str = ""
    wallabag_client_id: str = ""
    wallabag_client_secret: str = ""
    wallabag_password: str = ""
    wallabag_url: str = ""
    wallabag_username: str = ""

    model_config = SettingsConfigDict(env_prefix="importer_")
