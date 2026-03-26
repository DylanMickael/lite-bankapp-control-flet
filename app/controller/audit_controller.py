from app.db.database import SessionLocal
from app.db.models import AuditVirement
from sqlalchemy import func

class AuditController:
    @staticmethod
    def get_all(limit=20):
        db = SessionLocal()
        try:
            audits = db.query(AuditVirement).order_by(AuditVirement.date_operation.desc()).limit(limit).all()
            return audits
        finally:
            db.close()

    @staticmethod
    def get_counts():
        db = SessionLocal()
        try:
            # Query counts for each type of action
            results = db.query(AuditVirement.type_action, func.count(AuditVirement.id_audit)).group_by(AuditVirement.type_action).all()
            # Convert results to a dictionary
            counts = {action.lower(): count for action, count in results}
            return {
                "ajout": counts.get("ajout", 0),
                "modification": counts.get("modification", 0),
                "suppression": counts.get("suppression", 0)
            }
        finally:
            db.close()
