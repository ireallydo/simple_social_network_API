from sqlalchemy import Column, func, String, Integer, DateTime, ForeignKey, LargeBinary
from sqlalchemy.dialects.postgresql import UUID
from uuid import uuid4
from datetime import datetime
from sqlalchemy.orm import relationship
from db.models import BaseModel, UserModel


class PostModel(BaseModel):
    __tablename__ = 'tbl_posts'
    id = Column('id', UUID(as_uuid=True), unique=True, primary_key=True, default=uuid4)
    user_id = Column('user_id', UUID(as_uuid=True), ForeignKey('tbl_users.id', ondelete="CASCADE"))
    text = Column('text', String(255), nullable=True)
    image = Column('image', LargeBinary, nullable=True)
    likes = Column('likes', Integer, nullable=False, default=0)
    created_at = Column('created_at', DateTime, default=datetime.utcnow)
    updated_at = Column('updated_at', DateTime, default=datetime.utcnow, onupdate=func.current_timestamp())

    users = relationship('UserModel',
                         back_populates='posts',
                         lazy='subquery')

    liked_by = relationship('LikeModel',
                         back_populates='posts',
                         lazy='subquery')

    def dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}