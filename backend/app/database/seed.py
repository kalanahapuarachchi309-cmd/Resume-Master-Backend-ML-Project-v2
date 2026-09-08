"""Database Seeder for Default Users (Admin, Recruiter, Candidate)."""
import logging
from app.database.connection import SessionLocal
from app.models.user import User, UserRole
from app.core.security import get_password_hash

logger = logging.getLogger(__name__)

DEFAULT_USERS = [
    {
        "name": "System Admin",
        "email": "admin@resumemaster.com",
        "password": "Admin@123",
        "role": UserRole.ADMIN,
    },
    {
        "name": "Sarah Recruiter",
        "email": "recruiter@resumemaster.com",
        "password": "Recruiter@123",
        "role": UserRole.RECRUITER,
    },
    {
        "name": "Alex Candidate",
        "email": "candidate@resumemaster.com",
        "password": "Candidate@123",
        "role": UserRole.CANDIDATE,
    },
]


def seed_default_users():
    """Ensure default demo accounts exist for Admin, Recruiter, and Candidate."""
    db = SessionLocal()
    created_count = 0
    try:
        for user_data in DEFAULT_USERS:
            existing = db.query(User).filter(User.email == user_data["email"]).first()
            if not existing:
                user = User(
                    name=user_data["name"],
                    email=user_data["email"],
                    hashed_password=get_password_hash(user_data["password"]),
                    role=user_data["role"],
                )
                db.add(user)
                created_count += 1
                logger.info(f"Seeded user: {user_data['email']} ({user_data['role'].value})")
            else:
                logger.debug(f"User {user_data['email']} already exists.")
        db.commit()
        if created_count > 0:
            logger.info(f"Successfully seeded {created_count} default users.")
    except Exception as e:
        db.rollback()
        logger.error(f"Error seeding default users: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    from app.database.connection import init_db
    init_db()
    seed_default_users()
    print("Default users seeded successfully!")
