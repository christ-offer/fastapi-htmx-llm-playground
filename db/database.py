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

# Create functions for interacting with database

def create_user(username, password, email):
    new_user = User(username=username, password=password, email=email)
    session = SessionLocal()
    session.add(new_user)
    session.commit()
    session.close()
    return new_user

def login_user(username, password):
    session = SessionLocal()
    user = session.query(User).filter(User.username == username, User.password == password).first()
    session.close()
    return user

def get_user_conversations(user_id):
    session = SessionLocal()
    conversations = session.query(Conversation).join(Message).filter(Message.user_id == user_id).all()
    session.close()
    return conversations

def get_conversation_messages(conversation_id, user_id):
    session = SessionLocal()
    messages = session.query(Message).filter(Message.conversation_id == conversation_id, Message.user_id == user_id).all()
    session.close()
    return messages

def create_conversation(user_id, name):
    new_conversation = Conversation(user_id=user_id, name=name)
    session = SessionLocal()
    session.add(new_conversation)
    session.commit()
    session.close()
    return new_conversation

def add_message_to_conversation(user_id, conversation_id, role, content):
    # find the conversation with the matching id and user_id and add the message to it
    session = SessionLocal()
    conversation = session.query(Conversation).filter(Conversation.id == conversation_id, Conversation.user_id == user_id).first()
    new_message = Message(user_id=user_id, conversation_id=conversation_id, role=role, content=content)
    conversation.messages.append(new_message)
    session.commit()
    session.close()
    return new_message