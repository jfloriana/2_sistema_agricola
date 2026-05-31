from sqlalchemy import Column, Integer, String, Float, Boolean, Date, ForeignKey, DateTime
from sqlalchemy.sql import func
from database import Base

class Usuario(Base):
    __tablename__ = "usuarios"
    id_usuario = Column(Integer, primary_key=True, index=True)
    nombres = Column(String(100), nullable=False)
    apellidos = Column(String(100), nullable=False)
    correo = Column(String(100), unique=True, index=True, nullable=False)
    contrasena_hash = Column(String(255), nullable=False)
    rol = Column(String(50), default="Usuario")  # Admin, Usuario
    estado = Column(Boolean, default=True)

class Bitacora(Base):
    __tablename__ = "bitacora_sucesos"
    id_suceso = Column(Integer, primary_key=True, index=True)
    id_usuario = Column(Integer, ForeignKey("usuarios.id_usuario"))
    modulo = Column(String(100))
    accion = Column(String(255))
    fecha_hora = Column(DateTime, server_default=func.now())

class Cultivo(Base):
    __tablename__ = "cultivos"
    id_cultivo = Column(Integer, primary_key=True, index=True)
    nombre_cultivo = Column(String(100), nullable=False)
    variedad = Column(String(100))
    tiempo_estimado_cosecha_dias = Column(Integer)

class TokenRecuperacion(Base):
    __tablename__ = "tokens_recuperacion"
    id_token = Column(Integer, primary_key=True, index=True)
    id_usuario = Column(Integer, ForeignKey("usuarios.id_usuario"))
    token = Column(String(255), unique=True, index=True)
    expiracion = Column(DateTime, nullable=False)
    usado = Column(Boolean, default=False)