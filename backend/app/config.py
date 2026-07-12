import os

class Settings:
    PROJECT_NAME: str = "Sistema de planificacion de recursos empresariales"
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "postgresql://user:1234@localhost:5432/ERPDB",
    )
    FRONTEND_URL: str = os.getenv("FRONTEND_URL", "http://127.0.0.1:5173").rstrip("/")
    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "SUPER_SECRET_KEY_CHANGE_THIS")
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("JWT_ACCESS_TOKEN_EXPIRE_MINUTES", "480"))
    SMTP_USER: str = os.getenv("SMTP_USER", "")
    SMTP_PASSWORD: str = os.getenv("SMTP_PASSWORD", "")
    SMTP_HOST: str = os.getenv("SMTP_HOST", "smtp.zoho.com")
    SMTP_PORT: int = int(os.getenv("SMTP_PORT", "587"))

settings = Settings()
