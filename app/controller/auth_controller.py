from app.db.database import SessionLocal
from app.db.models import User

class AuthController:
    @staticmethod
    def login(username, password):
        db = SessionLocal()
        user = db.query(User).filter(User.username == username, User.password == password).first()
        db.close()
        return user

    @staticmethod
    def signin(username, password, role="user"):
        db = SessionLocal()
        # Check if exists
        existing = db.query(User).filter(User.username == username).first()
        if existing:
            db.close()
            return None, "Utilisateur déjà existant"
        
        new_user = User(username=username, password=password, role=role)
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        db.close()
        return new_user, "Compte créé"
