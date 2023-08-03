from sqlalchemy import Column, func, String, Integer, DateTime, ForeignKey, LargeBinary
from sqlalchemy.dialects.postgresql import UUID
from uuid import uuid4
from datetime import datetime
from sqlalchemy.orm import relationship
from db.models import BaseModel, UserModel


class LikeModel(BaseModel):
    __tablename__ = 'tbl_likes'
    id = Column('id', UUID(as_uuid=True), unique=True, primary_key=True, default=uuid4)
    user_id = Column('user_id', UUID(as_uuid=True), ForeignKey('tbl_users.id'))
    post_id = Column('post_id', UUID(as_uuid=True), ForeignKey('tbl_posts.id', ondelete='CASCADE'))
    created_at = Column('created_at', DateTime, default=datetime.utcnow)
    #
    # users = relationship('UserModel',
    #                      back_populates='liked_by',
    #                      lazy='subquery')

    posts = relationship('PostModel',
                         back_populates='liked_by',
                         lazy='subquery')

    def dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}