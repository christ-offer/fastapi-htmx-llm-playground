from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
import dotenv

envs = dotenv.dotenv_values()


DATABASE_URL = envs["SUPABASE_CONN"]

# Create SQLAlchemy engine

engine = create_engine(DATABASE_URL)
Base = declarative_base()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Define SQLAlchemy models
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, index=True)
    password = Column(String)
    email = Column(String, index=True)
    messages = relationship("Message", back_populates="user")
    conversations = relationship("Conversation", back_populates="user")

class Conversation(Base):
    __tablename__ = "conversations"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    user = relationship("User", back_populates="conversations")
    messages = relationship("Message", back_populates="conversation")

class Message(Base):
    __tablename__ = "messages"
    id = Column(Integer, primary_key=True, index=True)
    content = Column(String)
    role = Column(String)
    user_id = Column(Integer, ForeignKey("users.id"))
    conversation_id = Column(Integer, ForeignKey("conversations.id"))
    user = relationship("User", back_populates="messages")
    conversation = relationship("Conversation", back_populates="messages")

Base.metadata.create_all(bind=engine)

def get_db_session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_user(username, password, email):
    db = next(get_db_session())
    new_user = User(username=username, password=password, email=email)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

def login_user(username, password):
    db = next(get_db_session())
    user = db.query(User).filter(User.username == username, User.password == password).first()
    return user

def get_user_conversations(user_id):
    db = next(get_db_session())
    conversations = db.query(Conversation).filter(Conversation.user_id == user_id).all()
    return conversations

def get_conversation_messages(conversation_id, user_id):
    db = next(get_db_session())
    messages = db.query(Message).filter(Message.conversation_id == conversation_id, Message.user_id == user_id).all()
    return messages

def create_conversation(user_id, name):
    db = next(get_db_session())
    new_conversation = Conversation(user_id=user_id, name=name)
    db.add(new_conversation)
    db.commit()
    db.refresh(new_conversation)
    return new_conversation

def add_message_to_conversation(user_id, conversation_id, role, content):
    db = next(get_db_session())
    new_message = Message(user_id=user_id, conversation_id=conversation_id, role=role, content=content)
    db.add(new_message)
    db.commit()
    db.refresh(new_message)
    return new_message
