import os

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-key-123')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Construa o caminho absoluto para o diretório instance
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    INSTANCE_PATH = os.path.join(BASE_DIR, os.getenv('INSTANCE_PATH', 'instance'))
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(INSTANCE_PATH, 'tabacaria.db')

    UPLOAD_FOLDER = os.path.join(os.getcwd(), 'static', 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
