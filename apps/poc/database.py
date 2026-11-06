from sqlalchemy import create_engine, Numeric, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker
from decimal import Decimal

engine = create_engine('sqlite:///receipts.db', echo=True)
SessionLocal = sessionmaker(bind=engine)

class Base(DeclarativeBase):
    pass

class ReceiptModel(Base):
    __tablename__ = 'Receipt'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    company: Mapped[str] = mapped_column(String(150))
    total_value: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    date: Mapped[str] = mapped_column(String(10))

Base.metadata.create_all(bind=engine)

Session = sessionmaker(engine)