from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "VitaFlow"
    app_cn_name: str = "简历流"
    app_env: str = "development"
    app_host: str = "0.0.0.0"
    app_port: int = 8000
    app_debug: bool = True

    cors_origins: str = "http://localhost:5173,http://127.0.0.1:5173"

    db_host: str = "127.0.0.1"
    db_port: int = 3306
    db_user: str = "root"
    db_password: str = "123456"
    db_name: str = "vitaflow"
    db_charset: str = "utf8mb4"

    jwt_secret_key: str = "please_change_this_secret_key"
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 1440

    smtp_host: str = ""
    smtp_port: int = 465
    smtp_username: str = ""
    smtp_password: str = ""
    smtp_from_email: str = ""
    smtp_from_name: str = "VitaFlow"
    smtp_use_ssl: bool = True
    smtp_use_tls: bool = False
    smtp_timeout: int = 10
    email_code_expire_minutes: int = 10
    email_code_send_interval_seconds: int = 60

    ai_api_key: str = ""
    ai_base_url: str = "https://api.deepseek.com/v1"
    ai_model: str = "deepseek-chat"
    ai_temperature: float = 0.7
    ai_timeout: int = 60

    storage_provider: str = "minio"
    storage_public_url_mode: str = "proxy"

    minio_endpoint: str = "127.0.0.1:9000"
    minio_access_key: str = "minioadmin"
    minio_secret_key: str = "minioadmin"
    minio_bucket: str = "vitaflow"
    minio_secure: bool = False
    minio_public_url: str = "http://127.0.0.1:9000/vitaflow"

    aliyun_oss_endpoint: str = ""
    aliyun_oss_access_key_id: str = ""
    aliyun_oss_access_key_secret: str = ""
    aliyun_oss_bucket: str = ""
    aliyun_oss_public_url: str = ""
    aliyun_oss_secure: bool = True

    export_dir: str = "storage/exports"
    upload_dir: str = "storage/uploads"
    pdf_base_url: str = "http://127.0.0.1:8000"
    pdf_renderer: str = "chromium"
    pdf_chromium_executable_path: str = ""
    pdf_render_timeout_ms: int = 30000
    frontend_url: str = "http://localhost:5173"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    @property
    def database_url(self) -> str:
        return (
            f"mysql+pymysql://{self.db_user}:{self.db_password}"
            f"@{self.db_host}:{self.db_port}/{self.db_name}?charset={self.db_charset}"
        )

    @property
    def cors_origin_list(self) -> list[str]:
        return [item.strip() for item in self.cors_origins.split(",") if item.strip()]

    @property
    def backend_root(self) -> Path:
        return Path(__file__).resolve().parents[2]

    @property
    def export_path(self) -> Path:
        path = Path(self.export_dir)
        return path if path.is_absolute() else self.backend_root / path

    @property
    def upload_path(self) -> Path:
        path = Path(self.upload_dir)
        return path if path.is_absolute() else self.backend_root / path


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
