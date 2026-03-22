from sqlalchemy import text
from app.db.database import engine, SessionLocal
from app.db.models import Base, User, Client, Virement
import datetime

def setup_database():
    print("📦 Initialisation de la base de données...")
    
    # 1. Reset (Force) & Création des tables
    with engine.connect() as conn:
        conn.execute(text("DROP TABLE IF EXISTS audit_virement CASCADE;"))
        conn.execute(text("DROP TABLE IF EXISTS virement CASCADE;"))
        conn.execute(text("DROP TABLE IF EXISTS client CASCADE;"))
        conn.execute(text("DROP TABLE IF EXISTS users CASCADE;"))
        conn.commit()
    
    Base.metadata.create_all(bind=engine)
    print("✅ Tables recréées.")

    # 2. Injection des Triggers (Flattened Audit Version)
    print("⚙️  Injection des Triggers PostgreSQL...")
    with engine.connect() as conn:
        trigger_sql = """
        CREATE OR REPLACE FUNCTION audit_virement_logic() RETURNS TRIGGER AS $$
        DECLARE
            v_nom_client VARCHAR;
            v_solde_avnt FLOAT;
            v_solde_aprs FLOAT;
            v_compte_id INTEGER;
        BEGIN
            -- Determine target account
            IF (TG_OP = 'DELETE') THEN v_compte_id := OLD.num_compte;
            ELSE v_compte_id := NEW.num_compte; END IF;

            -- Capture 'Before' State
            SELECT nomclient, solde INTO v_nom_client, v_solde_avnt FROM client WHERE num_compte = v_compte_id;

            IF (TG_OP = 'INSERT') THEN
                UPDATE client SET solde = solde + NEW.montant WHERE num_compte = v_compte_id;
                SELECT solde INTO v_solde_aprs FROM client WHERE num_compte = v_compte_id;
                
                INSERT INTO audit_virement(type_action, num_virement, num_compte, nom_client, date_virement, montant_ancien, montant_nouv, utilisateur, date_operation)
                VALUES ('ajout', NEW.num_virement, v_compte_id, v_nom_client, NEW.date_virement, v_solde_avnt, v_solde_aprs, current_setting('app.current_user', true), NOW());
                RETURN NEW;

            ELSIF (TG_OP = 'UPDATE') THEN
                UPDATE client SET solde = solde - OLD.montant + NEW.montant WHERE num_compte = v_compte_id;
                SELECT solde INTO v_solde_aprs FROM client WHERE num_compte = v_compte_id;

                INSERT INTO audit_virement(type_action, num_virement, num_compte, nom_client, date_virement, montant_ancien, montant_nouv, utilisateur, date_operation)
                VALUES ('modification', NEW.num_virement, v_compte_id, v_nom_client, NEW.date_virement, v_solde_avnt, v_solde_aprs, current_setting('app.current_user', true), NOW());
                RETURN NEW;

            ELSIF (TG_OP = 'DELETE') THEN
                UPDATE client SET solde = solde - OLD.montant WHERE num_compte = v_compte_id;
                SELECT solde INTO v_solde_aprs FROM client WHERE num_compte = v_compte_id;

                INSERT INTO audit_virement(type_action, num_virement, num_compte, nom_client, date_virement, montant_ancien, montant_nouv, utilisateur, date_operation)
                VALUES ('suppression', OLD.num_virement, v_compte_id, v_nom_client, OLD.date_virement, v_solde_avnt, v_solde_aprs, current_setting('app.current_user', true), NOW());
                RETURN OLD;
            END IF;
        END;
        $$ LANGUAGE plpgsql;

        DROP TRIGGER IF EXISTS trg_virement_audit ON virement;
        CREATE TRIGGER trg_virement_audit
        AFTER INSERT OR UPDATE OR DELETE ON virement
        FOR EACH ROW EXECUTE FUNCTION audit_virement_logic();
        """
        conn.execute(text(trigger_sql))
        conn.commit()
    print("✅ Triggers opérationnels (Flattened Audit).")

    # 3. Seeding des données
    db = SessionLocal()
    try:
        # Création des utilisateurs
        admin = User(username="admin", password="admin123", role="admin")
        simple_user = User(username="dylan", password="password123", role="user")
        db.add_all([admin, simple_user])
        db.flush() 

        # Création du client Dylan
        simple_customer = Client(nomclient="Dylan Mickaël", solde=1000.0)
        db.add(simple_customer)
        db.flush()

        # --- VIREMENTS ---
        print("💸 Seeding des virements et déclenchement des triggers...")
        
        # 1. Virement ajouté par l'admin (500 €)
        db.execute(text("SELECT set_config('app.current_user', 'admin', false)"))
        v1 = Virement(num_compte=simple_customer.num_compte, montant=500.0)
        db.add(v1)
        db.flush() 

        # 2. Deux virements ajoutés par dylan (200 € et 300 €)
        db.execute(text("SELECT set_config('app.current_user', 'dylan', false)"))
        v2 = Virement(num_compte=simple_customer.num_compte, montant=200.0)
        v3 = Virement(num_compte=simple_customer.num_compte, montant=300.0)
        db.add_all([v2, v3])
        
        db.commit()
        print("✅ Seeding terminé.")
        print(f"💰 Solde final attendu pour Dylan : 2000.00 €")

    except Exception as e:
        print(f"❌ Erreur seeding: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    setup_database()