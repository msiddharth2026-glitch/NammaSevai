from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from ..database import get_db
from ..models import Scheme
from ..schemas import SchemeCreate, SchemeUpdate, SchemeResponse

router = APIRouter(prefix="/api/schemes", tags=["Schemes"])

@router.get("/", response_model=List[SchemeResponse])
def get_all_schemes(
    category: Optional[str] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(Scheme)
    if category and category != "all":
        query = query.filter(Scheme.category == category)
    if search:
        search_filter = f"%{search}%"
        query = query.filter(
            (Scheme.name.ilike(search_filter)) | 
            (Scheme.name_ta.ilike(search_filter)) |
            (Scheme.department.ilike(search_filter))
        )
    return query.all()

@router.get("/{scheme_id}", response_model=SchemeResponse)
def get_scheme_by_id(scheme_id: str, db: Session = Depends(get_db)):
    scheme = db.query(Scheme).filter(Scheme.id == scheme_id).first()
    if not scheme:
        raise HTTPException(status_code=404, detail="Scheme not found")
    return scheme

@router.post("/", response_model=SchemeResponse, status_code=201)
def create_scheme(payload: SchemeCreate, db: Session = Depends(get_db)):
    scheme_id = payload.id or f"scheme-{abs(hash(payload.name)) % 100000}"
    db_scheme = Scheme(id=scheme_id, **payload.dict(exclude={"id"}))
    db.add(db_scheme)
    db.commit()
    db.refresh(db_scheme)
    return db_scheme

@router.put("/{scheme_id}", response_model=SchemeResponse)
def update_scheme(scheme_id: str, payload: SchemeUpdate, db: Session = Depends(get_db)):
    scheme = db.query(Scheme).filter(Scheme.id == scheme_id).first()
    if not scheme:
        raise HTTPException(status_code=404, detail="Scheme not found")
    
    update_data = payload.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(scheme, key, value)
    
    db.commit()
    db.refresh(scheme)
    return scheme

@router.delete("/{scheme_id}")
def delete_scheme(scheme_id: str, db: Session = Depends(get_db)):
    scheme = db.query(Scheme).filter(Scheme.id == scheme_id).first()
    if not scheme:
        raise HTTPException(status_code=404, detail="Scheme not found")
    db.delete(scheme)
    db.commit()
    return {"message": "Scheme deleted successfully"}
