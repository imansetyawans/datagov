import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import SessionLocal, engine, Base
from app.models import User
import bcrypt


def seed_users():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        users_data = [
            {
                "email": "admin@datagov.local",
                "password": "admin123",
                "full_name": "Admin User",
                "role": "admin",
            },
            {
                "email": "editor@datagov.local",
                "password": "editor123",
                "full_name": "Editor User",
                "role": "editor",
            },
            {
                "email": "viewer@datagov.local",
                "password": "viewer123",
                "full_name": "Viewer User",
                "role": "viewer",
            },
        ]

        for user_data in users_data:
            existing = db.query(User).filter(User.email == user_data["email"]).first()
            if not existing:
                hashed = bcrypt.hashpw(user_data["password"].encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
                user = User(
                    email=user_data["email"],
                    hashed_password=hashed,
                    full_name=user_data["full_name"],
                    role=user_data["role"],
                    is_active=True,
                )
                db.add(user)
                print(f"Created user: {user_data['email']} ({user_data['role']})")
            else:
                print(f"User already exists: {user_data['email']}")

        db.commit()
        print("\nSeeding complete!")
        print("\nLogin credentials:")
        print("  Admin: admin@datagov.local / admin123")
        print("  Editor: editor@datagov.local / editor123")
        print("  Viewer: viewer@datagov.local / viewer123")

    except Exception as e:
        db.rollback()
        print(f"Error seeding database: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    seed_users()