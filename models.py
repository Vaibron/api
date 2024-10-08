from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True)
    path = Column(String)
    date = Column(DateTime)

class DocumentText(Base):
    __tablename__ = "documents_text"

    id = Column(Integer, primary_key=True)
    id_doc = Column(Integer, ForeignKey("documents.id"))
    text = Column(String)

    doc = relationship("Document", backref="texts")
