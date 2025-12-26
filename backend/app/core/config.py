import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# points to backend/app
BACKEND_DIR = os.path.dirname(BASE_DIR)
# points to backend/


class Settings:
    PROJECT_NAME: str = "AIMS-DS"
    MONGO_URI: str = "mongodb://localhost:27017"
    MONGO_DB_NAME: str = "aims_ds_db"


settings = Settings()
