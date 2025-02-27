from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import datetime

# Criar conexão com SQLite
DATABASE_URL = "sqlite:///instance/wayne_security.db"
engine = create_engine(DATABASE_URL, echo=True)
Base = declarative_base()

# Definir tabelas
class Item(Base):
    __tablename__ = "item"
    id = Column(Integer, primary_key=True, autoincrement=True)
    nome = Column(String(100), unique=True, nullable=False)
    quantidade_minima = Column(Float, nullable=False)
    quantidade_atual = Column(Float, nullable=False)
    unidade = Column(String(10), nullable=False)
    data_atualizacao = Column(DateTime, default=datetime.datetime.utcnow)

class User(Base):
    __tablename__ = "user"
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(100), unique=True, nullable=False)
    password_hash = Column(String(256), nullable=False)
    role = Column(String(20), nullable=False)

# Criar tabelas no banco
Base.metadata.create_all(engine)

print("Banco de dados recriado com sucesso!")