"""
Projects router - handles CRUD operations for projects.
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Optional
from datetime import date

from app.database import get_db
from app.models.user import User
from app.models.project import Project, ProjectStatus
from app.models.task import Task, TaskStatus
from app.schemas.project import ProjectCreate, ProjectUpdate, ProjectResponse, ProjectListResponse
from app.schemas.auth import MessageResponse
from app.utils.auth import get_current_user, require_admin

router = APIRouter(prefix="/api/projects", tags=["projects"])

@router.get("", response_model=ProjectListResponse)
async def get_projects(
    status_filter: Optional[str] = Query(None, alias="status", description="Filter by status"),
    user_id: Optional[int] = Query(None, description="Filter by user ID (admin only)"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Lấy danh sách dự án.
    
    - User thường chỉ thấy dự án của mình
    - Admin có thể thấy tất cả dự án hoặc filter theo user_id
    
    Args:
        status_filter: Lọc theo trạng thái (active/completed/on_hold)
        user_id: Lọc theo người sở hữu (chỉ admin)
        skip: Số lượng bản ghi bỏ qua
        limit: Số lượng bản ghi tối đa
        db: Database session
        current_user: Người dùng hiện tại
        
    Returns:
        ProjectListResponse: Danh sách dự án và tổng số
    """
    query = db.query(Project)
    
    # Apply authorization filter
    if current_user.role != "admin":
        # User chỉ xem projects của mình
        query = query.filter(Project.owner_id == current_user.id)
    else:
        # Admin có thể filter theo user_id
        if user_id:
            query = query.filter(Project.owner_id == user_id)
    
    # Apply status filter
    if status_filter:
        try:
            status_enum = ProjectStatus(status_filter)
            query = query.filter(Project.status == status_enum)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Trạng thái không hợp lệ. Chọn: active, completed, hoặc on_hold"
            )
    
    # Get total count
    total = query.count()
    
    # Get paginated results
    projects = query.offset(skip).limit(limit).all()
    
    # Enrich response with additional data
    projects_response = []
    for project in projects:
        # Count tasks
        total_tasks = db.query(Task).filter(Task.project_id == project.id).count()
        completed_tasks = db.query(Task).filter(
            Task.project_id == project.id,
            Task.status == TaskStatus.DONE
        ).count()
        
        # Get owner name
        owner = db.query(User).filter(User.id == project.owner_id).first()
        owner_name = owner.full_name if owner else None
        
        project_dict = {
            "id": project.id,
            "name": project.name,
            "description": project.description,
            "owner_id": project.owner_id,
            "owner_name": owner_name,
            "start_date": project.start_date,
            "end_date": project.end_date,
            "status": project.status.value,
            "total_tasks": total_tasks,
            "completed_tasks": completed_tasks,
            "created_at": project.created_at,
            "updated_at": project.updated_at
        }
        projects_response.append(ProjectResponse(**project_dict))
    
    return ProjectListResponse(projects=projects_response, total=total)

@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Lấy thông tin chi tiết một dự án.
    
    Args:
        project_id: ID của dự án
        db: Database session
        current_user: Người dùng hiện tại
        
    Returns:
        ProjectResponse: Thông tin dự án
        
    Raises:
        HTTPException 404: Nếu dự án không tồn tại
        HTTPException 403: Nếu không có quyền truy cập
    """
    project = db.query(Project).filter(Project.id == project_id).first()
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy dự án"
        )
    
    # Check authorization
    if current_user.role != "admin" and project.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Không có quyền truy cập dự án này"
        )
    
    # Enrich response
    total_tasks = db.query(Task).filter(Task.project_id == project.id).count()
    completed_tasks = db.query(Task).filter(
        Task.project_id == project.id,
        Task.status == TaskStatus.DONE
    ).count()
    
    owner = db.query(User).filter(User.id == project.owner_id).first()
    owner_name = owner.full_name if owner else None
    
    project_dict = {
        "id": project.id,
        "name": project.name,
        "description": project.description,
        "owner_id": project.owner_id,
        "owner_name": owner_name,
        "start_date": project.start_date,
        "end_date": project.end_date,
        "status": project.status.value,
        "total_tasks": total_tasks,
        "completed_tasks": completed_tasks,
        "created_at": project.created_at,
        "updated_at": project.updated_at
    }
    
    return ProjectResponse(**project_dict)

@router.post("", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
async def create_project(
    project_data: ProjectCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Tạo dự án mới.
    
    Dự án mới sẽ được gán cho người dùng hiện tại làm owner.
    
    Args:
        project_data: Thông tin dự án mới
        db: Database session
        current_user: Người dùng hiện tại
        
    Returns:
        ProjectResponse: Dự án vừa tạo
    """
    new_project = Project(
        name=project_data.name,
        description=project_data.description,
        owner_id=current_user.id,
        start_date=project_data.start_date,
        end_date=project_data.end_date,
        status=ProjectStatus.ACTIVE
    )
    
    db.add(new_project)
    db.commit()
    db.refresh(new_project)
    
    # Build response
    project_dict = {
        "id": new_project.id,
        "name": new_project.name,
        "description": new_project.description,
        "owner_id": new_project.owner_id,
        "owner_name": current_user.full_name,
        "start_date": new_project.start_date,
        "end_date": new_project.end_date,
        "status": new_project.status.value,
        "total_tasks": 0,
        "completed_tasks": 0,
        "created_at": new_project.created_at,
        "updated_at": new_project.updated_at
    }
    
    return ProjectResponse(**project_dict)

@router.put("/{project_id}", response_model=ProjectResponse)
async def update_project(
    project_id: int,
    project_data: ProjectUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Cập nhật thông tin dự án.
    
    Chỉ owner hoặc admin mới có thể cập nhật.
    
    Args:
        project_id: ID của dự án
        project_data: Thông tin cập nhật
        db: Database session
        current_user: Người dùng hiện tại
        
    Returns:
        ProjectResponse: Dự án đã cập nhật
        
    Raises:
        HTTPException 404: Nếu dự án không tồn tại
        HTTPException 403: Nếu không có quyền cập nhật
    """
    project = db.query(Project).filter(Project.id == project_id).first()
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy dự án"
        )
    
    # Check authorization
    if current_user.role != "admin" and project.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Không có quyền chỉnh sửa dự án này"
        )
    
    # Update fields
    update_data = project_data.model_dump(exclude_unset=True)
    if "status" in update_data:
        try:
            update_data["status"] = ProjectStatus(update_data["status"])
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Trạng thái không hợp lệ"
            )
    
    for field, value in update_data.items():
        setattr(project, field, value)
    
    db.commit()
    db.refresh(project)
    
    # Build response
    total_tasks = db.query(Task).filter(Task.project_id == project.id).count()
    completed_tasks = db.query(Task).filter(
        Task.project_id == project.id,
        Task.status == TaskStatus.DONE
    ).count()
    
    owner = db.query(User).filter(User.id == project.owner_id).first()
    owner_name = owner.full_name if owner else None
    
    project_dict = {
        "id": project.id,
        "name": project.name,
        "description": project.description,
        "owner_id": project.owner_id,
        "owner_name": owner_name,
        "start_date": project.start_date,
        "end_date": project.end_date,
        "status": project.status.value,
        "total_tasks": total_tasks,
        "completed_tasks": completed_tasks,
        "created_at": project.created_at,
        "updated_at": project.updated_at
    }
    
    return ProjectResponse(**project_dict)

@router.delete("/{project_id}", response_model=MessageResponse)
async def delete_project(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Xóa dự án.
    
    Chỉ owner hoặc admin mới có thể xóa.
    Xóa dự án sẽ xóa tất cả tasks liên quan (cascade delete).
    
    Args:
        project_id: ID của dự án
        db: Database session
        current_user: Người dùng hiện tại
        
    Returns:
        MessageResponse: Thông báo xóa thành công
        
    Raises:
        HTTPException 404: Nếu dự án không tồn tại
        HTTPException 403: Nếu không có quyền xóa
    """
    project = db.query(Project).filter(Project.id == project_id).first()
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy dự án"
        )
    
    # Check authorization
    if current_user.role != "admin" and project.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Không có quyền xóa dự án này"
        )
    
    db.delete(project)
    db.commit()
    
    return MessageResponse(
        message=f"Đã xóa dự án '{project.name}' thành công",
        success=True
    )

@router.post("/demo", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
async def create_demo_project(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Tạo dự án mẫu kèm tasks mẫu.
    
    Endpoint này được gọi từ n8n Flow 3 khi user mới đăng ký.
    Tạo 1 dự án với 3-5 tasks mẫu để user khám phá hệ thống.
    
    Args:
        db: Database session
        current_user: Người dùng hiện tại
        
    Returns:
        ProjectResponse: Dự án mẫu vừa tạo
    """
    from datetime import datetime, timedelta
    from app.models.task import Task, TaskStatus, TaskPriority
    
    # Create demo project
    demo_project = Project(
        name="Dự án mẫu - Khám phá hệ thống",
        description="Đây là dự án mẫu để bạn làm quen với hệ thống AI Deadline Forecasting. Hãy thử cập nhật tiến độ các task và xem dự đoán AI!",
        owner_id=current_user.id,
        start_date=date.today(),
        end_date=date.today() + timedelta(days=30),
        status=ProjectStatus.ACTIVE
    )
    
    db.add(demo_project)
    db.commit()
    db.refresh(demo_project)
    
    # Create demo tasks
    demo_tasks = [
        Task(
            project_id=demo_project.id,
            name="Khám phá Dashboard",
            description="Xem các biểu đồ và thống kê tổng quan",
            assigned_to=current_user.id,
            priority=TaskPriority.HIGH,
            status=TaskStatus.DONE,
            progress=100,
            estimated_hours=2,
            actual_hours=1.5,
            deadline=date.today() + timedelta(days=3)
        ),
        Task(
            project_id=demo_project.id,
            name="Tạo dự án thực tế",
            description="Tạo dự án đầu tiên của bạn",
            assigned_to=current_user.id,
            priority=TaskPriority.MEDIUM,
            status=TaskStatus.IN_PROGRESS,
            progress=50,
            estimated_hours=4,
            actual_hours=2,
            deadline=date.today() + timedelta(days=7)
        ),
        Task(
            project_id=demo_project.id,
            name="Thêm tasks vào dự án",
            description="Chia nhỏ công việc thành các task cụ thể",
            assigned_to=current_user.id,
            priority=TaskPriority.MEDIUM,
            status=TaskStatus.TODO,
            progress=0,
            estimated_hours=3,
            deadline=date.today() + timedelta(days=10)
        ),
        Task(
            project_id=demo_project.id,
            name="Cập nhật tiến độ task",
            description="Cập nhật progress để AI phân tích rủi ro",
            assigned_to=current_user.id,
            priority=TaskPriority.LOW,
            status=TaskStatus.TODO,
            progress=0,
            estimated_hours=1,
            deadline=date.today() + timedelta(days=14)
        ),
        Task(
            project_id=demo_project.id,
            name="Chạy mô phỏng kịch bản",
            description="Thử tính năng 'What-if' simulation",
            assigned_to=current_user.id,
            priority=TaskPriority.LOW,
            status=TaskStatus.TODO,
            progress=0,
            estimated_hours=2,
            deadline=date.today() + timedelta(days=20)
        )
    ]
    
    for task in demo_tasks:
        db.add(task)
    
    db.commit()
    
    # Build response
    project_dict = {
        "id": demo_project.id,
        "name": demo_project.name,
        "description": demo_project.description,
        "owner_id": demo_project.owner_id,
        "owner_name": current_user.full_name,
        "start_date": demo_project.start_date,
        "end_date": demo_project.end_date,
        "status": demo_project.status.value,
        "total_tasks": 5,
        "completed_tasks": 1,
        "created_at": demo_project.created_at,
        "updated_at": demo_project.updated_at
    }
    
    return ProjectResponse(**project_dict)
