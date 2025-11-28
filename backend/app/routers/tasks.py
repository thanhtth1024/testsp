"""
Tasks router - handles CRUD operations for tasks.
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime

from app.database import get_db
from app.models.user import User
from app.models.project import Project
from app.models.task import Task, TaskStatus, TaskPriority
from app.schemas.task import TaskCreate, TaskUpdate, TaskProgressUpdate, TaskResponse, TaskListResponse
from app.schemas.auth import MessageResponse
from app.utils.auth import get_current_user

router = APIRouter(prefix="/api/tasks", tags=["tasks"])

@router.get("", response_model=TaskListResponse)
async def get_tasks(
    project_id: Optional[int] = Query(None, description="Filter by project ID"),
    assigned_to: Optional[int] = Query(None, description="Filter by assigned user ID"),
    status_filter: Optional[str] = Query(None, alias="status", description="Filter by status"),
    priority: Optional[str] = Query(None, description="Filter by priority"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Lấy danh sách tasks.
    
    - User thường chỉ thấy tasks thuộc projects của mình hoặc được assign cho mình
    - Admin thấy tất cả tasks
    
    Args:
        project_id: Lọc theo dự án
        assigned_to: Lọc theo người được gán
        status_filter: Lọc theo trạng thái
        priority: Lọc theo độ ưu tiên
        skip: Số lượng bản ghi bỏ qua
        limit: Số lượng bản ghi tối đa
        db: Database session
        current_user: Người dùng hiện tại
        
    Returns:
        TaskListResponse: Danh sách tasks và tổng số
    """
    query = db.query(Task)
    
    # Apply authorization filter
    if current_user.role != "admin":
        # User xem tasks của projects mình sở hữu hoặc tasks được assign cho mình
        from sqlalchemy import or_
        query = query.join(Project).filter(
            or_(
                Project.owner_id == current_user.id,
                Task.assigned_to == current_user.id
            )
        )
    
    # Apply filters
    if project_id:
        query = query.filter(Task.project_id == project_id)
    
    if assigned_to:
        query = query.filter(Task.assigned_to == assigned_to)
    
    if status_filter:
        try:
            status_enum = TaskStatus(status_filter)
            query = query.filter(Task.status == status_enum)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Trạng thái không hợp lệ. Chọn: todo, in_progress, done, hoặc blocked"
            )
    
    if priority:
        try:
            priority_enum = TaskPriority(priority)
            query = query.filter(Task.priority == priority_enum)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Độ ưu tiên không hợp lệ. Chọn: low, medium, high, hoặc critical"
            )
    
    # Get total count
    total = query.count()
    
    # Get paginated results
    tasks = query.offset(skip).limit(limit).all()
    
    # Enrich response with additional data
    tasks_response = []
    for task in tasks:
        # Get assignee name
        assignee = db.query(User).filter(User.id == task.assigned_to).first() if task.assigned_to else None
        assigned_name = assignee.full_name if assignee else None
        
        # Get project name
        project = db.query(Project).filter(Project.id == task.project_id).first()
        project_name = project.name if project else None
        
        task_dict = {
            "id": task.id,
            "name": task.name,
            "description": task.description,
            "project_id": task.project_id,
            "project_name": project_name,
            "assigned_to": task.assigned_to,
            "assigned_name": assigned_name,
            "priority": task.priority.value,
            "status": task.status.value,
            "progress": int(task.progress),
            "estimated_hours": task.estimated_hours,
            "actual_hours": task.actual_hours,
            "deadline": task.deadline,
            "created_at": task.created_at,
            "updated_at": task.updated_at,
            "last_progress_update": task.last_progress_update
        }
        tasks_response.append(TaskResponse(**task_dict))
    
    return TaskListResponse(tasks=tasks_response, total=total)

@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Lấy thông tin chi tiết một task.
    
    Args:
        task_id: ID của task
        db: Database session
        current_user: Người dùng hiện tại
        
    Returns:
        TaskResponse: Thông tin task
        
    Raises:
        HTTPException 404: Nếu task không tồn tại
        HTTPException 403: Nếu không có quyền truy cập
    """
    task = db.query(Task).filter(Task.id == task_id).first()
    
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy task"
        )
    
    # Check authorization
    project = db.query(Project).filter(Project.id == task.project_id).first()
    if current_user.role != "admin":
        if not project or (project.owner_id != current_user.id and task.assigned_to != current_user.id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Không có quyền truy cập task này"
            )
    
    # Enrich response
    assignee = db.query(User).filter(User.id == task.assigned_to).first() if task.assigned_to else None
    assigned_name = assignee.full_name if assignee else None
    project_name = project.name if project else None
    
    task_dict = {
        "id": task.id,
        "name": task.name,
        "description": task.description,
        "project_id": task.project_id,
        "project_name": project_name,
        "assigned_to": task.assigned_to,
        "assigned_name": assigned_name,
        "priority": task.priority.value,
        "status": task.status.value,
        "progress": int(task.progress),
        "estimated_hours": task.estimated_hours,
        "actual_hours": task.actual_hours,
        "deadline": task.deadline,
        "created_at": task.created_at,
        "updated_at": task.updated_at,
        "last_progress_update": task.last_progress_update
    }
    
    return TaskResponse(**task_dict)

@router.post("", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(
    task_data: TaskCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Tạo task mới.
    
    Args:
        task_data: Thông tin task mới
        db: Database session
        current_user: Người dùng hiện tại
        
    Returns:
        TaskResponse: Task vừa tạo
        
    Raises:
        HTTPException 404: Nếu project không tồn tại
        HTTPException 403: Nếu không có quyền tạo task trong project
    """
    # Verify project exists and user has access
    project = db.query(Project).filter(Project.id == task_data.project_id).first()
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy dự án"
        )
    
    if current_user.role != "admin" and project.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Không có quyền tạo task trong dự án này"
        )
    
    # Verify assigned user exists (if provided)
    if task_data.assigned_to:
        assignee = db.query(User).filter(User.id == task_data.assigned_to).first()
        if not assignee:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Người dùng được gán không tồn tại"
            )
    
    # Create task
    try:
        new_task = Task(
            name=task_data.name,
            description=task_data.description,
            project_id=task_data.project_id,
            assigned_to=task_data.assigned_to,
            priority=TaskPriority(task_data.priority),
            status=TaskStatus(task_data.status),
            progress=0,
            estimated_hours=task_data.estimated_hours,
            deadline=task_data.deadline
        )
        
        db.add(new_task)
        db.commit()
        db.refresh(new_task)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Giá trị không hợp lệ: {str(e)}"
        )
    
    # Build response
    assignee = db.query(User).filter(User.id == new_task.assigned_to).first() if new_task.assigned_to else None
    assigned_name = assignee.full_name if assignee else None
    
    task_dict = {
        "id": new_task.id,
        "name": new_task.name,
        "description": new_task.description,
        "project_id": new_task.project_id,
        "project_name": project.name,
        "assigned_to": new_task.assigned_to,
        "assigned_name": assigned_name,
        "priority": new_task.priority.value,
        "status": new_task.status.value,
        "progress": int(new_task.progress),
        "estimated_hours": new_task.estimated_hours,
        "actual_hours": new_task.actual_hours,
        "deadline": new_task.deadline,
        "created_at": new_task.created_at,
        "updated_at": new_task.updated_at,
        "last_progress_update": new_task.last_progress_update
    }
    
    return TaskResponse(**task_dict)

@router.put("/{task_id}", response_model=TaskResponse)
async def update_task(
    task_id: int,
    task_data: TaskUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Cập nhật thông tin task.
    
    Args:
        task_id: ID của task
        task_data: Thông tin cập nhật
        db: Database session
        current_user: Người dùng hiện tại
        
    Returns:
        TaskResponse: Task đã cập nhật
        
    Raises:
        HTTPException 404: Nếu task không tồn tại
        HTTPException 403: Nếu không có quyền cập nhật
    """
    task = db.query(Task).filter(Task.id == task_id).first()
    
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy task"
        )
    
    # Check authorization
    project = db.query(Project).filter(Project.id == task.project_id).first()
    if current_user.role != "admin":
        if not project or (project.owner_id != current_user.id and task.assigned_to != current_user.id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Không có quyền chỉnh sửa task này"
            )
    
    # Update fields
    update_data = task_data.model_dump(exclude_unset=True)
    
    try:
        if "priority" in update_data:
            update_data["priority"] = TaskPriority(update_data["priority"])
        if "status" in update_data:
            update_data["status"] = TaskStatus(update_data["status"])
        
        # Update progress timestamp if progress changed
        if "progress" in update_data:
            update_data["last_progress_update"] = datetime.utcnow()
        
        for field, value in update_data.items():
            setattr(task, field, value)
        
        db.commit()
        db.refresh(task)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Giá trị không hợp lệ: {str(e)}"
        )
    
    # Build response
    assignee = db.query(User).filter(User.id == task.assigned_to).first() if task.assigned_to else None
    assigned_name = assignee.full_name if assignee else None
    project_name = project.name if project else None
    
    task_dict = {
        "id": task.id,
        "name": task.name,
        "description": task.description,
        "project_id": task.project_id,
        "project_name": project_name,
        "assigned_to": task.assigned_to,
        "assigned_name": assigned_name,
        "priority": task.priority.value,
        "status": task.status.value,
        "progress": int(task.progress),
        "estimated_hours": task.estimated_hours,
        "actual_hours": task.actual_hours,
        "deadline": task.deadline,
        "created_at": task.created_at,
        "updated_at": task.updated_at,
        "last_progress_update": task.last_progress_update
    }
    
    return TaskResponse(**task_dict)

@router.patch("/{task_id}/progress", response_model=TaskResponse)
async def update_task_progress(
    task_id: int,
    progress_data: TaskProgressUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Cập nhật tiến độ task.
    
    Endpoint đặc biệt để cập nhật nhanh tiến độ và timestamp.
    
    Args:
        task_id: ID của task
        progress_data: Tiến độ mới (0-100)
        db: Database session
        current_user: Người dùng hiện tại
        
    Returns:
        TaskResponse: Task đã cập nhật
        
    Raises:
        HTTPException 404: Nếu task không tồn tại
        HTTPException 403: Nếu không có quyền cập nhật
    """
    task = db.query(Task).filter(Task.id == task_id).first()
    
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy task"
        )
    
    # Check authorization
    project = db.query(Project).filter(Project.id == task.project_id).first()
    if current_user.role != "admin":
        if not project or (project.owner_id != current_user.id and task.assigned_to != current_user.id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Không có quyền cập nhật task này"
            )
    
    # Update progress and timestamp
    task.progress = progress_data.progress
    task.last_progress_update = datetime.utcnow()
    
    # Auto-update status based on progress
    if progress_data.progress == 100 and task.status != TaskStatus.DONE:
        task.status = TaskStatus.DONE
    elif progress_data.progress > 0 and task.status == TaskStatus.TODO:
        task.status = TaskStatus.IN_PROGRESS
    
    db.commit()
    db.refresh(task)
    
    # Build response
    assignee = db.query(User).filter(User.id == task.assigned_to).first() if task.assigned_to else None
    assigned_name = assignee.full_name if assignee else None
    project_name = project.name if project else None
    
    task_dict = {
        "id": task.id,
        "name": task.name,
        "description": task.description,
        "project_id": task.project_id,
        "project_name": project_name,
        "assigned_to": task.assigned_to,
        "assigned_name": assigned_name,
        "priority": task.priority.value,
        "status": task.status.value,
        "progress": int(task.progress),
        "estimated_hours": task.estimated_hours,
        "actual_hours": task.actual_hours,
        "deadline": task.deadline,
        "created_at": task.created_at,
        "updated_at": task.updated_at,
        "last_progress_update": task.last_progress_update
    }
    
    return TaskResponse(**task_dict)

@router.delete("/{task_id}", response_model=MessageResponse)
async def delete_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Xóa task.
    
    Chỉ project owner hoặc admin mới có thể xóa.
    
    Args:
        task_id: ID của task
        db: Database session
        current_user: Người dùng hiện tại
        
    Returns:
        MessageResponse: Thông báo xóa thành công
        
    Raises:
        HTTPException 404: Nếu task không tồn tại
        HTTPException 403: Nếu không có quyền xóa
    """
    task = db.query(Task).filter(Task.id == task_id).first()
    
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy task"
        )
    
    # Check authorization
    project = db.query(Project).filter(Project.id == task.project_id).first()
    if current_user.role != "admin":
        if not project or project.owner_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Không có quyền xóa task này"
            )
    
    task_name = task.name
    db.delete(task)
    db.commit()
    
    return MessageResponse(
        message=f"Đã xóa task '{task_name}' thành công",
        success=True
    )
