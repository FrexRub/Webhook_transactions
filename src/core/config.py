import logging
from pathlib import Path

from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).parent.parent.parent

COOKIE_NAME = "bonds_score"


def configure_logging(level=logging.INFO):
    logging.basicConfig(
        level=level,
        datefmt="%Y-%m-%d %H:%M:%S",
        format="[%(asctime)s.%(msecs)03d] %(module)10s:%(lineno)-3d %(levelname)-7s - %(message)s",
    )


class SettingConn(BaseSettings):
    postgres_user: str
    postgres_password: str
    postgres_db: str
    postgres_host: str = "localhost"
    postgres_port: int

    SECRET_KEY: str

    model_config = SettingsConfigDict(env_file=BASE_DIR / ".env")


setting_conn = SettingConn()


class DbSetting(BaseSettings):
    url: str = (
        f"postgresql+asyncpg://{setting_conn.postgres_user}:{setting_conn.postgres_password}@{setting_conn.postgres_host}:{setting_conn.postgres_port}/{setting_conn.postgres_db}"
    )
    echo: bool = False


class AuthJWT(BaseModel):
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60


class Setting(BaseSettings):
    db: DbSetting = DbSetting()
    auth_jwt: AuthJWT = AuthJWT()


setting = Setting()
