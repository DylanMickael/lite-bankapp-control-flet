from app.db.database import SessionLocal
from app.db.models import AuditVirement

class AuditController:
    @staticmethod
    def get_all(limit=20):
        db = SessionLocal()
        audits = db.query(AuditVirement).order_by(AuditVirement.date_operation.desc()).limit(limit).all()
        db.close()
        return audits
