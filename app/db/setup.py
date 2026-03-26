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
        print("🌱 Seeding des utilisateurs et clients...")
        # Création des utilisateurs demandés
        admin = User(username="admin", password="admin123", role="admin")
        u1 = User(username="user1", password="user123", role="user")
        u2 = User(username="user2", password="user456", role="user")
        
        db.add_all([admin, u1, u2])
        
        # Création du client cible
        customer = Client(nomclient="John Doe", solde=1000.0)
        db.add(customer)
        db.flush() # Pour récupérer les IDs

        print("💸 Exécution des virements par les utilisateurs...")

        # --- OPERATION USER 1 ---
        # On définit l'utilisateur courant pour le trigger PostgreSQL
        db.execute(text("SELECT set_config('app.current_user', 'user1', false)"))
        v1 = Virement(num_compte=customer.num_compte, montant=500.0)
        db.add(v1)
        db.flush() 
        print(" -> 1 virement effectué par user1 (500Ar)")

        # --- OPERATIONS USER 2 ---
        db.execute(text("SELECT set_config('app.current_user', 'user2', false)"))
        v2 = Virement(num_compte=customer.num_compte, montant=200.0)
        v3 = Virement(num_compte=customer.num_compte, montant=300.0)
        db.add_all([v2, v3])
        print(" -> 2 virements effectués par user2 (200Ar et 300Ar)")
        
        db.commit()
        print("✅ Seeding terminé avec succès.")
        print(f"💰 Solde final de John Doe : 2000.00 Ar (1000 initial + 1000 virements)")

    except Exception as e:
        print(f"❌ Erreur seeding: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    setup_database()