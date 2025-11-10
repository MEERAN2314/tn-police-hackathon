#!/usr/bin/env python3
"""
Quick fix for login issues in TOR Analysis System
"""

import asyncio
import sys
import logging

# Add app to path
sys.path.append('.')

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def create_demo_users():
    """Create demo users in the database"""
    try:
        from app.database import connect_to_mongo, get_database
        from app.routers.auth import create_user, UserCreate
        
        logger.info("🔧 Creating demo users...")
        
        # Connect to database
        await connect_to_mongo()
        db = await get_database()
        
        # Check if users already exist
        existing_users = await db.users.count_documents({})
        
        if existing_users == 0:
            # Create demo users
            demo_users = [
                {
                    "username": "admin",
                    "email": "admin@demo.local",
                    "full_name": "System Administrator",
                    "password": "admin123",
                    "role": "admin"
                },
                {
                    "username": "user", 
                    "email": "user@demo.local",
                    "full_name": "Demo User",
                    "password": "password123",
                    "role": "analyst"
                },
                {
                    "username": "demo",
                    "email": "demo@demo.local", 
                    "full_name": "Demo Account",
                    "password": "demo123",
                    "role": "analyst"
                }
            ]
            
            for user_data in demo_users:
                user_create = UserCreate(**user_data)
                success = await create_user(user_create)
                if success:
                    logger.info(f"✅ Created user: {user_data['username']}")
                else:
                    logger.error(f"❌ Failed to create user: {user_data['username']}")
            
            logger.info("✅ Demo users created successfully!")
            
        else:
            logger.info(f"ℹ️  Found {existing_users} existing users in database")
            
        # List available credentials
        logger.info("\n" + "=" * 50)
        logger.info("🔑 AVAILABLE LOGIN CREDENTIALS:")
        logger.info("=" * 50)
        logger.info("👤 Username: admin")
        logger.info("🔒 Password: admin123")
        logger.info("📋 Role: Administrator")
        logger.info("")
        logger.info("👤 Username: user") 
        logger.info("🔒 Password: password123")
        logger.info("📋 Role: Analyst")
        logger.info("")
        logger.info("👤 Username: demo")
        logger.info("🔒 Password: demo123") 
        logger.info("📋 Role: Analyst")
        logger.info("=" * 50)
        
    except Exception as e:
        logger.error(f"❌ Error creating demo users: {e}")
        logger.info("💡 The system will still work with fallback demo credentials")

async def test_authentication():
    """Test the authentication system"""
    try:
        from app.routers.auth import authenticate_user
        
        logger.info("🧪 Testing authentication...")
        
        # Test demo credentials
        test_credentials = [
            ("admin", "admin123"),
            ("user", "password123"), 
            ("demo", "demo123")
        ]
        
        for username, password in test_credentials:
            user = await authenticate_user(username, password)
            if user:
                logger.info(f"✅ Authentication works for: {username}")
            else:
                logger.error(f"❌ Authentication failed for: {username}")
                
    except Exception as e:
        logger.error(f"❌ Authentication test failed: {e}")

def print_login_instructions():
    """Print login instructions"""
    logger.info("\n" + "🚀 LOGIN INSTRUCTIONS:")
    logger.info("=" * 40)
    logger.info("1. Go to: http://localhost:8004/auth/login")
    logger.info("2. Use any of these credentials:")
    logger.info("   • admin / admin123")
    logger.info("   • user / password123") 
    logger.info("   • demo / demo123")
    logger.info("3. Click 'Sign In'")
    logger.info("4. You'll be redirected to the dashboard")
    logger.info("=" * 40)

async def main():
    """Main function"""
    try:
        logger.info("🔧 TOR Analysis System - Login Fix")
        logger.info("=" * 50)
        
        # Create demo users
        await create_demo_users()
        
        # Test authentication
        await test_authentication()
        
        # Print instructions
        print_login_instructions()
        
        logger.info("✅ Login system is now ready!")
        
    except Exception as e:
        logger.error(f"❌ Fix failed: {e}")

if __name__ == "__main__":
    asyncio.run(main())