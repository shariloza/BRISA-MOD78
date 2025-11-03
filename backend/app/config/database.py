from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import os

# Cargar variables del .env
load_dotenv()

# URL de la base de datos
DATABASE_URL = os.getenv("DATABASE_URL") or "mysql+pymysql://root:@localhost:3306/bienestar_estudiantil"

# Motor de conexión
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    echo=True  # Mostrar queries en consola (solo desarrollo)
)

# Sesión
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base para los modelos
Base = declarative_base()

# Dependencia para endpoints FastAPI
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
