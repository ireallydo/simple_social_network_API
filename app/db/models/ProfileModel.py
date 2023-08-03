from sqlalchemy import Column, func, String, DateTime, Date, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
from sqlalchemy.orm import relationship
from db.models import BaseModel, UserModel


class ProfileModel(BaseModel):
    __tablename__ = 'tbl_profiles'
    id = Column('id', UUID(as_uuid=True),
                ForeignKey('tbl_users.id', ondelete="CASCADE"),
                unique=True, primary_key=True)
    first_name = Column('first_name', String(255), nullable=False)
    second_name = Column('second_name', String(255), default=None)
    last_name = Column('last_name', String(255), nullable=False)
    birth_date = Column('birth_date', Date, nullable=False)
    about = Column('about', String(255), default=None)
    created_at = Column('created_at', DateTime, default=datetime.utcnow)
    updated_at = Column('updated_at', DateTime, default=datetime.utcnow, onupdate=func.current_timestamp())

    users = relationship('UserModel',
                         back_populates='profiles',
                         lazy='subquery')

    def dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}
