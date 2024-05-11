from fastapi import FastAPI, Depends, HTTPException, Security
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import sessionmaker
from fastapi.middleware.cors import CORSMiddleware
from typing import List
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from pydantic import BaseModel
from typing import Optional
from sqlalchemy import Column, Integer, String, Boolean
import firebase_admin
from firebase_admin import credentials, auth
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials


security = HTTPBearer()

def get_current_user(credential: HTTPAuthorizationCredentials = Security(security)):
    token: credential.credentials

    try:
        decoded_token = auth.verify_id_token(token)
        uid = decoded_token['uid']
        return uid
    except Exception as e:
        raise HTTPException(status_code=401, detail="Invalid authentication credentials")



cred_path = credentials.Certificate('todo-gita-firebase-adminsdk-xl91z-cb5dfed5d0.json')
firebase_admin.initialize_app(cred_path)

app = FastAPI()

DATABASE_URL = "mysql+asyncmy://root:@localhost/ToDo"

engine = create_async_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine, class_=AsyncSession)
Base = declarative_base()



class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    firebase_uid = Column(String(255), index=True, nullable=False)
    email = Column(String(255), index=True, nullable=False)
    username = Column(String(255), index=True, nullable=False)


class Task(Base):
    __tablename__ = 'tasks'

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    title = Column(String(255), index=True, nullable=False)
    completed = Column(Boolean, default=False)
    user_id = Column(Integer, index=True, nullable=False)



async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

@app.on_event("startup")
async def startup_event():
    await create_tables()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  
    allow_credentials=True,
    allow_methods=["*"],  
    allow_headers=["*"],  
)



class TaskSchema(BaseModel):
    id: Optional[int] = None
    title: str
    completed: bool = False
    user_id: int

    class Config:
        orm_mode = True


class UserSchema(BaseModel):
    firebase_uid: str
    email: str
    username: str

class LoginSchema(BaseModel):
    firebase_uid: str
 


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/register", response_model=UserSchema)
async def register_user(user_data: UserSchema, db: AsyncSession = Depends(get_db)):
    try:
        new_user = User(**user_data.dict())
        db.add(new_user)
        await db.commit()
        await db.refresh(new_user)
        return new_user
    except Exception as e:
        await db.rollback()
        print(f"Failed to register user: {str(e)}")
        # Raise an HTTPException with status code 500
        raise HTTPException(status_code=500, detail="Failed to create user")

    
@app.post("/login", response_model=UserSchema)
async def login_user(login_data: LoginSchema, db: AsyncSession = Depends(get_db)):
    firebase_uid = login_data.firebase_uid
    try:
        async with db as session:
            existing_user = await session.execute(select(User).where(User.firebase_uid == firebase_uid))
            user = existing_user.scalars().first()
            if not user:
                raise HTTPException(status_code=404, detail="User not found")
            return user
    except Exception as e:
        print(f"Failed to login user: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to login user")

@app.post("/tasks", response_model=TaskSchema)
async def create_task(task: TaskSchema, db: AsyncSession = Depends(get_db)):
    db_task = Task(**task.dict())
    db.add(db_task)
    await db.commit()
    await db.refresh(db_task)
    return db_task

@app.get("/tasks", response_model=List[TaskSchema])
async def read_tasks(db: AsyncSession = Depends(get_db)):
    async with db as session:
        result = await session.execute(select(Task))
        tasks = result.scalars().all()
        return tasks

@app.get("/tasks/{task_id}", response_model=TaskSchema)
async def read_task(uid: str = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    async with db as session:
        result = await session.execute(select(Task).where(Task.user_id == uid))
        task = result.scalars().first()
        if task is None:
            raise HTTPException(status_code=404, detail="Task not found")
        return task

@app.put("/tasks/{task_id}", response_model=TaskSchema)
async def update_task(task_id: int, task_update: TaskSchema, db: AsyncSession = Depends(get_db)):
    async with db as session:
        result = await session.execute(select(Task).where(Task.id == task_id))
        task = result.scalars().first()
        if task is None:
            raise HTTPException(status_code=404, detail="Task not found")
        
        task_data = task_update.dict(exclude_unset=True)
        for key, value in task_data.items():
            setattr(task, key, value)

        await session.commit()
        return task

@app.delete("/tasks/{task_id}", status_code=204)
async def delete_task(task_id: int, db: AsyncSession = Depends(get_db)):
    async with db as session:
        result = await session.execute(select(Task).where(Task.id == task_id))
        task = result.scalars().first()
        if task is None:
            raise HTTPException(status_code=404, detail="Task not found")

        await session.delete(task)
        await session.commit()