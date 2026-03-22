from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
import datetime

Base = declarative_base()

class Client(Base):
    __tablename__ = 'client'
    num_compte = Column(Integer, primary_key=True)
    nomclient = Column(String)
    solde = Column(Float, default=0.0)

class Virement(Base):
    __tablename__ = 'virement'
    num_virement = Column(Integer, primary_key=True, autoincrement=True)
    num_compte = Column(Integer, ForeignKey('client.num_compte'))
    montant = Column(Float)
    date_virement = Column(DateTime, default=datetime.datetime.now)

class AuditVirement(Base):
    __tablename__ = 'audit_virement'
    id_audit = Column(Integer, primary_key=True, autoincrement=True)
    type_action = Column(String) # 'ajout', 'suppression', 'modification'
    date_operation = Column(DateTime, default=datetime.datetime.now)
    num_virement = Column(Integer)
    num_compte = Column(Integer)
    nom_client = Column(String)
    date_virement = Column(DateTime, default=datetime.datetime.now)
    montant_ancien = Column(Float)
    montant_nouv = Column(Float)
    utilisateur = Column(String)

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String, unique=True)
    password = Column(String)
    role = Column(String) # 'admin' or 'user'