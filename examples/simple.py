import random
from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from sqlalchemy import (
    Column,
    ForeignKey,
    Integer,
    String,
    create_engine,
    event,
    select,
    text,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session, relationship, sessionmaker

from fastapi_rowsecurity.main import (
    Everyone,
    Permissive,
    UserOwnerInt,
    set_rls_policies,
)

# Create a Faker instance
# fake = Faker()

# engine = create_engine("postgresql://postgres:postgres@0.0.0.0:5432/test")
engine = create_engine("postgresql://app_db_write:V11Xn3#c3$4r@0.0.0.0:5432/test")
Base = declarative_base()


@event.listens_for(Base.metadata, "after_create")
def receive_after_create(target, connection, tables, **kw):
    set_rls_policies(Base, connection, False)


app = FastAPI()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True, index=True)
    password = Column(String)

    items = relationship("Item", back_populates="owner")


class Item(Base):
    __tablename__ = "items"

    id = Column(Integer, primary_key=True)
    title = Column(String, index=True)
    description = Column(String, index=True)
    owner_id = Column(Integer, ForeignKey("users.id"))

    owner = relationship("User", back_populates="items")

    @classmethod
    def __rls_policies__(cls):
        return [
            Permissive(principal=Everyone, policy="SELECT"),
            Permissive(principal=UserOwnerInt, policy=["INSERT", "UPDATE", "DELETE"]),
        ]


def get_session(token: Annotated[str, Depends(oauth2_scheme)]) -> Session:
    username = token
    Session = sessionmaker(bind=engine, expire_on_commit=False)
    with Session() as session:
        user = session.execute(select(User).where(User.username == username)).scalars().one_or_none()
        try:
            session.execute(text(f"SET app.current_user_id = {user.id}"))  # attach to the session
            return session
        except:
            session.rollback()
            raise
        finally:
            print("RESET")
            session.execute(text("RESET ROLE;"))
            session.commit()
            session.close()
            pass


def get_current_user(token: Annotated[str, Depends(oauth2_scheme)], session: Session = Depends(get_session)):
    username = token
    user = session.execute(select(User).where(User.username == username)).scalars().one_or_none()
    return user


@app.post("/token")
async def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], session: Session = Depends(get_session)):
    username = form_data.username
    password = form_data.password
    user = session.execute(select(User).where(User.username == username)).scalars().one_or_none()
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    if not password == user.password:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    return {"access_token": user.username, "token_type": "bearer"}


class ItemCreate(BaseModel):
    title: str
    description: str | None = None


@app.post("/items")
def create(
    item: ItemCreate, current_user: Annotated[User, Depends(get_current_user)], session: Session = Depends(get_session)
):
    db_item = Item(**item.model_dump(), owner_id=current_user.id)
    session.add(db_item)
    session.commit()


# @app.post("/items/{item_id}")
# def update(item_id: int, session: Session = Depends(get_session)):
#     db_item = session.query(Item).filter(Item.id == item_id).first()
#     if db_item is None:
#         raise HTTPException(status_code=404, detail="Item not found")
#     db_item.title = fake.sentence(nb_words=random.randint(2, 4))
#     db_item.description = fake.paragraph()
#     session.commit()


@app.delete("/items/{item_id}")
def delete(item_id: int, session: Session = Depends(get_session)):
    db_item = session.query(Item).filter(Item.id == item_id).first()
    if db_item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    session.delete(db_item)
    session.commit()


@app.get("/items")
def root(session: Session = Depends(get_session)):
    statement = select(Item)
    results = session.execute(statement)
    return results.scalars().all()
