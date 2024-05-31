from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

# Для тестов
#URL_DATABASE = 'postgresql://postgres:qwerty22@localhost:5432/test_users_achievements'
#engine = create_engine(URL_DATABASE)
#SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Подключение к базе данных
URL_DATABASE = 'postgresql://postgres:qwerty22@db:5432/users_achievements'

# Движок SQLAlchemy для управления подключением к базе данных
engine = create_engine(URL_DATABASE)

# Сессия SQLAlchemy для взаимодействия с базой данных
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Базовый класс для определения моделей SQLAlchemy
Base = declarative_base()