"""Standalone Script to Seed Default Admin, Recruiter, and Candidate Accounts."""
import sys
import os

# Add backend directory to sys.path
backend_path = os.path.join(os.path.dirname(__file__), "backend")
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

from app.database.connection import init_db
from app.database.seed import seed_default_users, DEFAULT_USERS

def main():
    print("Initializing database tables...")
    init_db()
    print("Seeding default accounts...")
    seed_default_users()
    print("\n" + "=" * 55)
    print("   DEFAULT ACCOUNTS READY TO LOGIN")
    print("=" * 55)
    for u in DEFAULT_USERS:
        print(f"Role:     {u['role'].value}")
        print(f"Name:     {u['name']}")
        print(f"Email:    {u['email']}")
        print(f"Password: {u['password']}")
        print("-" * 55)

if __name__ == "__main__":
    main()
