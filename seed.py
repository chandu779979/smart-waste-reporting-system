from app import create_app
from extensions import db
from models.municipality import Municipality

MUNICIPALITIES_LIST = [
    "Anantapur Municipality",
    "Kadapa Municipality",
    "Kurnool Municipality",
    "Nandyal Municipality",
    "Rajampet Municipality",
    "Proddatur Municipality",
    "Tadipatri Municipality",
    "Hindupur Municipality",
    "Madanapalle Municipality",
    "Chittoor Municipality",
    "Srikakulam Municipality",
    "Vizianagaram Municipality",
    "Tadepalligudem Municipality",
    "Eluru Municipality",
    "Amalapuram Municipality",
    "Bhimavaram Municipality",
    "Machilipatnam Municipality",
    "Tenali Municipality",
    "Ongole Municipality",
    "Adoni Municipality"
]

def seed_db():
    app = create_app()
    with app.app_context():
        # Auto-create tables (safe fallback if migrations are run or not)
        db.create_all()
        
        print("Initializing seed of 20 municipalities...")
        seeded_count = 0
        for name in MUNICIPALITIES_LIST:
            existing = Municipality.query.filter_by(name=name).first()
            if not existing:
                municipality = Municipality(name=name)
                db.session.add(municipality)
                seeded_count += 1
                
        db.session.commit()
        print(f"Successfully completed! Seeded {seeded_count} municipalities.")

if __name__ == '__main__':
    seed_db()
