from datetime import datetime
from sqlalchemy import Column, DateTime, Integer, BigInteger, String
from sqlalchemy.ext.asyncio import create_async_engine, AsyncAttrs, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from data.config import ECHO_DATABASE

engine = create_async_engine(url='sqlite+aiosqlite:///db.sqlite3', echo=ECHO_DATABASE)

async_session = async_sessionmaker(engine)

def abstract_class(cls):
    cls.__abstract__ = True
    return cls


@abstract_class
class Base(AsyncAttrs, DeclarativeBase):
    id = Column(Integer, primary_key=True, autoincrement=True)
    created_at = Column(DateTime, default=datetime.now)



class User(Base):
    __tablename__ = 'users'

    tg_id = Column(BigInteger, unique=True)
    tg_username = Column(String, nullable=False)
    role = Column(String, nullable=False)


class Tag(Base):
    __tablename__ = 'tags'

    name = Column(String, nullable=False)


class Voice_actor(Base):
    __tablename__ = 'voice_actors'

    name = Column(String, nullable=False)
    link = Column(String, nullable=False)

class Editor(Base):
    __tablename__ = 'editors'

    name = Column(String, nullable=False)
    link = Column(String, nullable=False)


async def async_main():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)