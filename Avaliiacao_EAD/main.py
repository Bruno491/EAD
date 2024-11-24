from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, Boolean, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
import datetime

DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class Cliente(Base):
    __tablename__ = "clientes"
    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, index=True)
    tipo = Column(String(1))
    data_de_chegada = Column(DateTime, default=datetime.datetime.utcnow)
    atendido = Column(Boolean, default=False)

Base.metadata.create_all(bind=engine)

app = FastAPI()

# Configuração de CORS
origins = [
    "http://localhost",
    "http://127.0.0.1",
    "http://127.0.0.1:5500",  # Porta do seu servidor de desenvolvimento front-end, se necessário
    "null"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ClienteCreate(BaseModel):
    nome: str
    tipo: str

class ClienteResponse(BaseModel):
    id: int
    nome: str
    tipo: str
    data_de_chegada: datetime.datetime
    atendido: bool

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/fila", response_model=list[ClienteResponse])
def read_fila(db: Session = Depends(get_db)):
    clientes = db.query(Cliente).filter(Cliente.atendido == False).all()
    return clientes

@app.get("/fila/{id}", response_model=ClienteResponse)
def read_cliente(id: int, db: Session = Depends(get_db)):
    cliente = db.query(Cliente).filter(Cliente.id == id).first()
    if cliente is None:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")
    return cliente

@app.post("/fila", response_model=ClienteResponse)
def create_cliente(cliente: ClienteCreate, db: Session = Depends(get_db)):
    if len(cliente.nome) > 20 or cliente.tipo not in ["N", "P"]:
        raise HTTPException(status_code=400, detail="Dados inválidos")
    db_cliente = Cliente(nome=cliente.nome, tipo=cliente.tipo)
    db.add(db_cliente)
    db.commit()
    db.refresh(db_cliente)
    return db_cliente

@app.put("/fila")
def update_fila(db: Session = Depends(get_db)):
    clientes = db.query(Cliente).filter(Cliente.atendido == False).order_by(Cliente.id).all()
    for idx, cliente in enumerate(clientes):
        cliente.id = idx + 1
        if cliente.id == 1:
            cliente.atendido = True
    db.commit()
    return {"message": "Fila atualizada"}

@app.put("/fila/atendido/{id}")
def atender_cliente(id: int, db: Session = Depends(get_db)):
    cliente = db.query(Cliente).filter(Cliente.id == id).first()
    if cliente is None:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")
    cliente.atendido = True
    db.commit()
    return {"message": "Cliente atendido"}

@app.delete("/fila/{id}")
def delete_cliente(id: int, db: Session = Depends(get_db)):
    cliente = db.query(Cliente).filter(Cliente.id == id).first()
    if cliente is None:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")
    db.delete(cliente)
    db.commit()
    # Atualizar as posições dos clientes restantes
    clientes = db.query(Cliente).filter(Cliente.atendido == False).order_by(Cliente.id).all()
    for idx, cliente in enumerate(clientes):
        cliente.id = idx + 1
    db.commit()
    return {"message": "Cliente removido"}

