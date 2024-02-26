from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import declarative_base, relationship

from fastapi_rowsecurity import Permissive, set_rls_policies
from fastapi_rowsecurity.principals import Authenticated, UserOwner

Base = declarative_base()
set_rls_policies(Base)


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True, index=True)
    items = relationship("Item", back_populates="owner")


class Item(Base):
    __tablename__ = "items"

    id = Column(Integer, primary_key=True)
    title = Column(String, index=True)
    owner_id = Column(Integer, ForeignKey("users.id"))
    owner = relationship("User", back_populates="items")

    @classmethod
    def __rls_policies__(cls):
        return [
            Permissive(principal=Authenticated, policy="SELECT"),
            Permissive(principal=UserOwner, policy=["INSERT", "UPDATE", "DELETE"]),
        ]
