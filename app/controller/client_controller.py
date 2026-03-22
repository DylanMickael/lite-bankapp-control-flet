from app.db.database import SessionLocal
from app.db.models import Client

class ClientController:
    @staticmethod
    def get_all():
        db = SessionLocal()
        clients = db.query(Client).order_by(Client.num_compte).all()
        db.close()
        return clients

    @staticmethod
    def create(nom, solde=0.0):
        db = SessionLocal()
        new_client = Client(nomclient=nom, solde=solde)
        db.add(new_client)
        db.commit()
        db.refresh(new_client)
        db.close()
        return new_client

    @staticmethod
    def update(num, nom, solde):
        db = SessionLocal()
        client = db.query(Client).filter(Client.num_compte == num).first()
        if client:
            client.nomclient = nom
            client.solde = solde
            db.commit()
            db.refresh(client)
        db.close()
        return client

    @staticmethod
    def delete(num):
        db = SessionLocal()
        client = db.query(Client).filter(Client.num_compte == num).first()
        if client:
            db.delete(client)
            db.commit()
        db.close()
        return True
