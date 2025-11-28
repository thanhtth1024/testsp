"""
Seed script to populate database with sample data.
Creates users, projects, and tasks for testing.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from datetime import datetime, timedelta
from app.database import SessionLocal, engine
from app.models import (
    User, UserRole,
    Project, ProjectStatus,
    Task, TaskStatus, TaskPriority
)
from passlib.context import CryptContext

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def seed_data():
    """Seed the database with sample data"""
    db = SessionLocal()
    
    try:
        print("🌱 Starting database seeding...")
        
        # Check if data already exists
        existing_users = db.query(User).count()
        if existing_users > 0:
            print("⚠️  Database already has data. Skipping seed.")
            return
        
        # Create users
        print("👥 Creating users...")
        users = [
            User(
                email="admin@ai-deadline.io.vn",
                username="admin",
                full_name="System Administrator",
                password_hash=hash_password("admin123"),
                role=UserRole.ADMIN,
                created_at=datetime.utcnow()
            ),
            User(
                email="nguyen.van.a@company.com",
                username="nguyenvana",
                full_name="Nguyễn Văn A",
                password_hash=hash_password("password123"),
                role=UserRole.USER,
                created_at=datetime.utcnow()
            ),
            User(
                email="tran.thi.b@company.com",
                username="tranthib",
                full_name="Trần Thị B",
                password_hash=hash_password("password123"),
                role=UserRole.USER,
                created_at=datetime.utcnow()
            ),
        ]
        
        for user in users:
            db.add(user)
        db.commit()
        print(f"✅ Created {len(users)} users")
        
        # Create projects
        print("📁 Creating projects...")
        today = datetime.utcnow()
        projects = [
            Project(
                name="Website Redesign 2024",
                description="Thiết kế lại giao diện website công ty với UI/UX hiện đại",
                owner_id=users[1].id,
                status=ProjectStatus.ACTIVE,
                start_date=today - timedelta(days=10),
                end_date=today + timedelta(days=20),
                created_at=today - timedelta(days=10),
                updated_at=today
            ),
            Project(
                name="Mobile App Development",
                description="Phát triển ứng dụng mobile cho iOS và Android",
                owner_id=users[1].id,
                status=ProjectStatus.ACTIVE,
                start_date=today - timedelta(days=15),
                end_date=today + timedelta(days=45),
                created_at=today - timedelta(days=15),
                updated_at=today
            ),
            Project(
                name="AI Chatbot Integration",
                description="Tích hợp AI chatbot vào hệ thống hỗ trợ khách hàng",
                owner_id=users[2].id,
                status=ProjectStatus.ACTIVE,
                start_date=today - timedelta(days=5),
                end_date=today + timedelta(days=25),
                created_at=today - timedelta(days=5),
                updated_at=today
            ),
            Project(
                name="Database Migration",
                description="Di chuyển database từ MySQL sang PostgreSQL",
                owner_id=users[2].id,
                status=ProjectStatus.ON_HOLD,
                start_date=today - timedelta(days=30),
                end_date=today + timedelta(days=10),
                created_at=today - timedelta(days=30),
                updated_at=today
            ),
            Project(
                name="API Documentation",
                description="Hoàn thiện tài liệu API cho hệ thống",
                owner_id=users[1].id,
                status=ProjectStatus.COMPLETED,
                start_date=today - timedelta(days=60),
                end_date=today - timedelta(days=5),
                created_at=today - timedelta(days=60),
                updated_at=today
            ),
        ]
        
        for project in projects:
            db.add(project)
        db.commit()
        print(f"✅ Created {len(projects)} projects")
        
        # Create tasks
        print("📝 Creating tasks...")
        tasks = [
            # Website Redesign tasks
            Task(
                name="Thiết kế mockup trang chủ",
                description="Tạo mockup cho trang chủ với Figma",
                project_id=projects[0].id,
                assigned_to=users[1].id,
                status=TaskStatus.DONE,
                priority=TaskPriority.HIGH,
                progress=100.0,
                deadline=today + timedelta(days=2),
                last_progress_update=today - timedelta(hours=12),
                created_at=today - timedelta(days=9)
            ),
            Task(
                name="Phát triển Frontend trang chủ",
                description="Code React components cho trang chủ",
                project_id=projects[0].id,
                assigned_to=users[2].id,
                status=TaskStatus.IN_PROGRESS,
                priority=TaskPriority.HIGH,
                progress=65.0,
                deadline=today + timedelta(days=5),
                last_progress_update=today - timedelta(hours=2),
                created_at=today - timedelta(days=7)
            ),
            Task(
                name="Tích hợp API Backend",
                description="Kết nối Frontend với API Backend",
                project_id=projects[0].id,
                assigned_to=users[2].id,
                status=TaskStatus.TODO,
                priority=TaskPriority.MEDIUM,
                progress=0.0,
                deadline=today + timedelta(days=10),
                last_progress_update=today - timedelta(days=5),
                created_at=today - timedelta(days=5)
            ),
            
            # Mobile App tasks
            Task(
                name="Setup React Native project",
                description="Khởi tạo project React Native",
                project_id=projects[1].id,
                assigned_to=users[1].id,
                status=TaskStatus.DONE,
                priority=TaskPriority.CRITICAL,
                progress=100.0,
                deadline=today - timedelta(days=5),
                last_progress_update=today - timedelta(days=6),
                created_at=today - timedelta(days=15)
            ),
            Task(
                name="Phát triển màn hình đăng nhập",
                description="UI và logic cho màn hình đăng nhập",
                project_id=projects[1].id,
                assigned_to=users[1].id,
                status=TaskStatus.IN_PROGRESS,
                priority=TaskPriority.HIGH,
                progress=80.0,
                deadline=today + timedelta(days=3),
                last_progress_update=today - timedelta(hours=4),
                created_at=today - timedelta(days=10)
            ),
            Task(
                name="Tích hợp Firebase Authentication",
                description="Setup Firebase cho authentication",
                project_id=projects[1].id,
                assigned_to=users[2].id,
                status=TaskStatus.IN_PROGRESS,
                priority=TaskPriority.HIGH,
                progress=40.0,
                deadline=today + timedelta(days=7),
                last_progress_update=today - timedelta(hours=18),
                created_at=today - timedelta(days=8)
            ),
            Task(
                name="Phát triển màn hình Dashboard",
                description="UI dashboard với charts và stats",
                project_id=projects[1].id,
                assigned_to=users[1].id,
                status=TaskStatus.TODO,
                priority=TaskPriority.MEDIUM,
                progress=0.0,
                deadline=today + timedelta(days=15),
                last_progress_update=today - timedelta(days=8),
                created_at=today - timedelta(days=5)
            ),
            
            # AI Chatbot tasks
            Task(
                name="Research AI models",
                description="Nghiên cứu các AI models phù hợp",
                project_id=projects[2].id,
                assigned_to=users[2].id,
                status=TaskStatus.DONE,
                priority=TaskPriority.HIGH,
                progress=100.0,
                deadline=today - timedelta(days=2),
                last_progress_update=today - timedelta(days=3),
                created_at=today - timedelta(days=5)
            ),
            Task(
                name="Setup Gemini API integration",
                description="Tích hợp Gemini API vào backend",
                project_id=projects[2].id,
                assigned_to=users[2].id,
                status=TaskStatus.IN_PROGRESS,
                priority=TaskPriority.CRITICAL,
                progress=55.0,
                deadline=today + timedelta(days=2),
                last_progress_update=today - timedelta(minutes=30),
                created_at=today - timedelta(days=3)
            ),
            Task(
                name="Tạo Chat UI component",
                description="Component giao diện chat trong app",
                project_id=projects[2].id,
                assigned_to=users[1].id,
                status=TaskStatus.IN_PROGRESS,
                priority=TaskPriority.HIGH,
                progress=30.0,
                deadline=today + timedelta(days=5),
                last_progress_update=today - timedelta(hours=6),
                created_at=today - timedelta(days=2)
            ),
            Task(
                name="Testing và Fine-tuning",
                description="Test chatbot và điều chỉnh prompts",
                project_id=projects[2].id,
                assigned_to=users[2].id,
                status=TaskStatus.TODO,
                priority=TaskPriority.MEDIUM,
                progress=0.0,
                deadline=today + timedelta(days=12),
                last_progress_update=today - timedelta(days=2),
                created_at=today - timedelta(days=1)
            ),
            
            # Database Migration tasks
            Task(
                name="Backup MySQL database",
                description="Full backup trước khi migrate",
                project_id=projects[3].id,
                assigned_to=users[1].id,
                status=TaskStatus.DONE,
                priority=TaskPriority.CRITICAL,
                progress=100.0,
                deadline=today - timedelta(days=15),
                last_progress_update=today - timedelta(days=16),
                created_at=today - timedelta(days=25)
            ),
            Task(
                name="Setup PostgreSQL server",
                description="Cài đặt và config PostgreSQL",
                project_id=projects[3].id,
                assigned_to=users[2].id,
                status=TaskStatus.TODO,
                priority=TaskPriority.HIGH,
                progress=0.0,
                deadline=today + timedelta(days=5),
                last_progress_update=today - timedelta(days=10),
                created_at=today - timedelta(days=20)
            ),
            
            # API Documentation tasks
            Task(
                name="Viết API documentation",
                description="Tài liệu tất cả endpoints với OpenAPI",
                project_id=projects[4].id,
                assigned_to=users[1].id,
                status=TaskStatus.DONE,
                priority=TaskPriority.MEDIUM,
                progress=100.0,
                deadline=today - timedelta(days=10),
                last_progress_update=today - timedelta(days=11),
                created_at=today - timedelta(days=40)
            ),
            Task(
                name="Deploy documentation site",
                description="Deploy docs lên hosting",
                project_id=projects[4].id,
                assigned_to=users[2].id,
                status=TaskStatus.DONE,
                priority=TaskPriority.LOW,
                progress=100.0,
                deadline=today - timedelta(days=7),
                last_progress_update=today - timedelta(days=8),
                created_at=today - timedelta(days=35)
            ),
        ]
        
        for task in tasks:
            db.add(task)
        db.commit()
        print(f"✅ Created {len(tasks)} tasks")
        
        print("\n✨ Database seeding completed successfully!")
        print("\n📊 Summary:")
        print(f"   - Users: {len(users)}")
        print(f"   - Projects: {len(projects)}")
        print(f"   - Tasks: {len(tasks)}")
        print("\n🔐 Login credentials:")
        print("   Admin: admin / admin123")
        print("   User 1: nguyenvana / password123")
        print("   User 2: tranthib / password123")
        
    except Exception as e:
        print(f"❌ Error seeding database: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    seed_data()
