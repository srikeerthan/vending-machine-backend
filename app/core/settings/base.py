from pydantic_settings import SettingsConfigDict, BaseSettings


class BaseAppSettings(BaseSettings):
    """
    Base application setting class.
    """
    model_config = SettingsConfigDict(env_file=".env")
