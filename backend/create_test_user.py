"""
Script to create a test user for development.
Run this to bypass registration issues.
"""
from db.base import SessionLocal
from models.user import User
from core.security import get_password_hash

def create_test_user():
    """Create a test user with email: test@example.com, password: test123"""
    db = SessionLocal()
    try:
        # Check if user already exists
        existing = db.query(User).filter(User.email == "test@example.com").first()
        if existing:
            print("✓ Test user already exists!")
            print(f"  Email: test@example.com")
            print(f"  Password: test123")
            return
        
        # Create test user
        test_user = User(
            email="test@example.com",
            hashed_password=get_password_hash("test123")
        )
        db.add(test_user)
        db.commit()
        db.refresh(test_user)
        
        print("✓ Test user created successfully!")
        print(f"  Email: test@example.com")
        print(f"  Password: test123")
        print(f"  User ID: {test_user.id}")
    except Exception as e:
        print(f"✗ Error creating test user: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    create_test_user()





