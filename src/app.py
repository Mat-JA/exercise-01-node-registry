"""
Exercise 01 — Node Registry API

Implement a FastAPI application with the following endpoints:

GET    /health          → health check with DB status
POST   /api/nodes       → register a new node
GET    /api/nodes       → list all nodes
GET    /api/nodes/{name} → get a node by name
PUT    /api/nodes/{name} → update a node
DELETE /api/nodes/{name} → soft-delete a node (set status=inactive)

See README.md for full specification.
"""

from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError
from datetime import datetime

from . import models, schemas
from .database import engine, get_db

app = FastAPI(title="Node Registry API")

# Create tables
models.Base.metadata.create_all(bind=engine)

@app.get("/health")
def health_check(db: Session = Depends(get_db)):
    try:
        count = db.query(models.Node).filter(models.Node.status == "active").count()
        return {"status": "ok", "db": "connected", "nodes_count": count}
    except Exception:
        return {"status": "ok", "db": "disconnected", "nodes_count": 0}

@app.post("/api/nodes", status_code=status.HTTP_201_CREATED, response_model=schemas.NodeResponse)
def create_node(node: schemas.NodeCreate, db: Session = Depends(get_db)):
    existing_node = db.query(models.Node).filter_by(name=node.name).first()
    if existing_node:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Node already registered"
        )
    
    db_node = models.Node(
        name=node.name,
        host=node.host,
        port=node.port,
        status="active"
    )
    db.add(db_node)
    try:
        db.commit()
        db.refresh(db_node)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Node already registered"
        )
    return db_node

@app.get("/api/nodes", response_model=list[schemas.NodeResponse])
def list_nodes(db: Session = Depends(get_db)):
    return db.query(models.Node).all()

@app.get("/api/nodes/{name}", response_model=schemas.NodeResponse)
def get_node(name: str, db: Session = Depends(get_db)):
    node = db.query(models.Node).filter_by(name=name).first()
    if not node:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Node not found"
        )
    return node

@app.put("/api/nodes/{name}", response_model=schemas.NodeResponse)
def update_node(name: str, node_update: schemas.NodeUpdate, db: Session = Depends(get_db)):
    node = db.query(models.Node).filter_by(name=name).first()
    if not node:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Node not found"
        )
    
    update_data = node_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(node, key, value)
    
    node.updated_at = datetime.utcnow()
    
    try:
        db.commit()
        db.refresh(node)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Update conflicts with an existing node"
        )
    return node

@app.delete("/api/nodes/{name}", status_code=status.HTTP_204_NO_CONTENT)
def delete_node(name: str, db: Session = Depends(get_db)):
    node = db.query(models.Node).filter_by(name=name).first()
    if not node:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Node not found"
        )
    
    node.status = "inactive"
    db.commit()
    return None
