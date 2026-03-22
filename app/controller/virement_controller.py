from app.db.database import SessionLocal
from app.db.models import Virement
from sqlalchemy import text
import datetime

class VirementController:
    @staticmethod
    def get_all():
        db = SessionLocal()
        virements = db.query(Virement).order_by(Virement.date_virement.desc()).all()
        db.close()
        return virements

    @staticmethod
    def create(num_compte, montant, current_user_name):
        db = SessionLocal()
        try:
            db.execute(text(f"SELECT set_config('app.current_user', '{current_user_name}', false)"))
            new_v = Virement(num_compte=num_compte, montant=montant, date_virement=datetime.datetime.now())
            db.add(new_v)
            db.commit()
            db.refresh(new_v)
            db.close()
            return new_v
        except Exception as e:
            db.rollback()
            db.close()
            raise e

    @staticmethod
    def update(num_v, num_compte, montant, current_user_name):
        db = SessionLocal()
        try:
            db.execute(text(f"SELECT set_config('app.current_user', '{current_user_name}', false)"))
            v = db.query(Virement).filter(Virement.num_virement == num_v).first()
            if v:
                v.num_compte = num_compte
                v.montant = montant
                db.commit()
                db.refresh(v)
            db.close()
            return v
        except Exception as e:
            db.rollback()
            db.close()
            raise e

    @staticmethod
    def delete(num_v, current_user_name):
        db = SessionLocal()
        try:
            db.execute(text(f"SELECT set_config('app.current_user', '{current_user_name}', false)"))
            v = db.query(Virement).filter(Virement.num_virement == num_v).first()
            if v:
                db.delete(v)
                db.commit()
            db.close()
            return True
        except Exception as e:
            db.rollback()
            db.close()
            raise e
