from pydantic import field_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    APP_MODE: str = "full"  # full=内网全功能 | public=公网只读问答
    DATABASE_URL: str = "postgresql+psycopg://aiqa:aiqa_dev_password@localhost:5432/aiqa"
    SECRET_KEY: str = "please-change-me"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7
    DEEPSEEK_API_KEY: str = ""
    PUBLIC_API_TOKEN: str = ""
    UPLOAD_DIR: str = "./data/uploads"
    MAX_IMAGE_MB: int = 10
    MAX_VIDEO_MB: int = 100
    MAX_PDF_MB: int = 50

    @field_validator("SECRET_KEY")
    @classmethod
    def check_secret_key(cls, v: str) -> str:
        if v in ("please-change-me", "change-me", ""):
            raise ValueError("SECRET_KEY 不能使用默认值，请在 backend/.env 中设置强随机值")
        return v

    model_config = {"env_file": ".env"}


settings = Settings()
