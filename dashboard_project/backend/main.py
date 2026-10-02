from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List

import models, schemas
from database import engine, get_db

# Create DB tables on startup
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Interactive Dashboard API")

# Enable Cross-Origin Resource Sharing (CORS)
# This allows your Streamlit frontend on port 8501 to send requests to FastAPI on port 8000
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/metrics", response_model=List[schemas.MetricResponse])
def get_metrics(db: Session = Depends(get_db)):
    return db.query(models.MetricModel).all()

@app.post("/metrics", response_model=schemas.MetricResponse, status_code=status.HTTP_201_CREATED)
def create_metric(metric: schemas.MetricCreate, db: Session = Depends(get_db)):
    db_metric = models.MetricModel(**metric.model_dump())
    db.add(db_metric)
    db.commit()
    db.refresh(db_metric)
    return db_metric

@app.delete("/metrics/{metric_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_metric(metric_id: int, db: Session = Depends(get_db)):
    metric = db.query(models.MetricModel).filter(models.MetricModel.id == metric_id).first()
    if not metric:
        raise HTTPException(status_code=404, detail="Metric not found")
    db.delete(metric)
    db.commit()
    return

# Simple Analytics forecast calculation endpoint
@app.get("/analytics/forecast/{metric_id}")
def forecast_metric(metric_id: int, db: Session = Depends(get_db)):
    metric = db.query(models.MetricModel).filter(models.MetricModel.id == metric_id).first()
    if not metric:
        raise HTTPException(status_code=404, detail="Metric not found")
    
    # 15% growth calculation
    projected = round(metric.value * 1.15, 2)
    return {
        "metric_name": metric.name,
        "current_value": metric.value,
        "projected_growth_15pct": projected
    }