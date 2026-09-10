from functools import lru_cache
from urllib.parse import quote_plus

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str
    app_env: str
    app_host: str
    app_port: int
    db_server: str
    db_name: str
    db_driver: str
    db_trusted_connection: str
    db_trust_server_certificate: str

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    def database_url(self, database: str | None = None) -> str:
        connection = (
            f"DRIVER={{{self.db_driver}}};"
            f"SERVER={self.db_server};"
            f"DATABASE={database or self.db_name};"
            f"Trusted_Connection={self.db_trusted_connection};"
            f"TrustServerCertificate={self.db_trust_server_certificate};"
        )
        return f"mssql+pyodbc:///?odbc_connect={quote_plus(connection)}"


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
