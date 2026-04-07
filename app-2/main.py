from fastapi import FastAPI, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from db import get_session
from models import DMI, BME280, DS18B20, SCD41
from schemas import MeasurementBase, Station
from typing import List, Optional
from datetime import datetime

app = FastAPI(title="Weather station API")

def normalize_measurements(dmis: List[DMI],
                           bme: List[BME280],
                           ds18: List[DS18B20],
                           scd: List[SCD41]) -> List[dict]:
    results = []

    # --- DMI ---
    for r in dmis:
        results.append({
            "station_id": r.station_id,
            "sensor": "DMI",
            "location": None,
            "parameter": r.parameter_id,
            "value": float(r.value),
            "observed_at": r.observed_at
        })

    # --- BME280 ---
    for r in bme:
        for param in ["temperature", "humidity", "pressure"]:
            val = getattr(r, param)
            if val is not None:
                results.append({
                    "station_id": r.reader_id,
                    "sensor": "BME280",
                    "location": r.location,
                    "parameter": param,
                    "value": float(val),
                    "observed_at": r.observed_at
                })

    # --- DS18B20 ---
    for r in ds18:
        if r.temperature is not None:
            results.append({
                "station_id": r.reader_id,
                "sensor": "DS18B20",
                "location": r.location,
                "parameter": "temperature",
                "value": float(r.temperature),
                "observed_at": r.observed_at
            })

    # --- SCD41 ---
    for r in scd:
        for param in ["temperature", "humidity", "co2"]:
            val = getattr(r, param)
            if val is not None:
                results.append({
                    "station_id": r.reader_id,
                    "sensor": "SCD41",
                    "location": None,
                    "parameter": param,
                    "value": float(val),
                    "observed_at": r.observed_at
                })

    return results

# --- Helper: parse datetime from query parameter ---
def parse_datetime(dt_str: str) -> datetime:
	try:
		return datetime.fromisoformat(dt_str)
	except ValueError:
		raise HTTPException(status_code=400, detail=f"Invalid datetime format: {dt_str}. Use ISO format.")


# --- Endpoint 1: List stations ---
@app.get("/stations", response_model=List[Station])
def get_stations(db: Session = Depends(get_session)):
	stations = db.query(DMI.station_id).distinct().all()
	return [{"station_id": s.station_id, "name": None} for s in stations]


# --- Endpoint 2: Measurements for one station with filters ---
@app.get("/stations/{station_id}/measurements", response_model=List[MeasurementBase])
def get_measurements(
    station_id: int,
    from_: Optional[str] = Query(None, alias="from"),
    to: Optional[str] = Query(None),
    type_: Optional[str] = Query(None, alias="type"),
    db: Session = Depends(get_session)
):
    from_dt = parse_datetime(from_) if from_ else None
    to_dt = parse_datetime(to) if to else None

    # --- DMI ---
    query_dmi = db.query(DMI).filter(DMI.station_id == station_id)
    if from_dt:
        query_dmi = query_dmi.filter(DMI.observed_at >= from_dt)
    if to_dt:
        query_dmi = query_dmi.filter(DMI.observed_at <= to_dt)
    if type_ and type_ in ["temperature", "humidity", "pressure"]:
        query_dmi = query_dmi.filter(DMI.parameter_id == type_)
    dmis = query_dmi.all()

    # --- BME280 ---
    query_bme = db.query(BME280).filter(BME280.reader_id == station_id)
    if from_dt:
        query_bme = query_bme.filter(BME280.observed_at >= from_dt)
    if to_dt:
        query_bme = query_bme.filter(BME280.observed_at <= to_dt)
    bmes = query_bme.all()

    # --- DS18B20 ---
    query_ds = db.query(DS18B20).filter(DS18B20.reader_id == station_id)
    if from_dt:
        query_ds = query_ds.filter(DS18B20.observed_at >= from_dt)
    if to_dt:
        query_ds = query_ds.filter(DS18B20.observed_at <= to_dt)
    ds18s = query_ds.all()

    # --- SCD41 ---
    query_scd = db.query(SCD41).filter(SCD41.reader_id == station_id)
    if from_dt:
        query_scd = query_scd.filter(SCD41.observed_at >= from_dt)
    if to_dt:
        query_scd = query_scd.filter(SCD41.observed_at <= to_dt)
    if type_ and type_ in ["temperature", "humidity", "co2"]:
        query_scd = query_scd.filter(getattr(SCD41, type_) != None)
    scds = query_scd.all()

    results = normalize_measurements(dmis, bmes, ds18s, scds)
    if type_:
        results = [r for r in results if r["parameter"] == type_]

    return results


# --- Endpoint 3: Latest measurement per station ---
@app.get("/stations/latest", response_model=List[MeasurementBase])
def get_latest_measurements(db: Session = Depends(get_session)):
    # DMI: seneste per station og parameter
    dmis = db.query(DMI).distinct(DMI.station_id, DMI.parameter_id).order_by(DMI.station_id, DMI.parameter_id, DMI.observed_at.desc()).all()
    # BME280
    bmes = db.query(BME280).order_by(BME280.reader_id, BME280.observed_at.desc()).all()
    # DS18B20
    ds18s = db.query(DS18B20).order_by(DS18B20.reader_id, DS18B20.observed_at.desc()).all()
    # SCD41
    scds = db.query(SCD41).order_by(SCD41.reader_id, SCD41.observed_at.desc()).all()

    results = normalize_measurements(dmis, bmes, ds18s, scds)
    # Optional: fjern dubletter, behold kun seneste pr station+parameter
    latest = {}
    for r in results:
        key = (r["station_id"], r["parameter"])
        if key not in latest or r["observed_at"] > latest[key]["observed_at"]:
            latest[key] = r

    return list(latest.values())

# --- Endpoint 4: Compare across stations ---
@app.get("/measurements/compare", response_model=List[MeasurementBase])
def compare_measurements(
    from_: Optional[str] = Query(None, alias="from"),
    to: Optional[str] = Query(None),
    type_: Optional[str] = Query(None, alias="type"),
    db: Session = Depends(get_session)
):
    from_dt = parse_datetime(from_) if from_ else None
    to_dt = parse_datetime(to) if to else None

    # Alle tabeller
    dmis = db.query(DMI).all()
    bmes = db.query(BME280).all()
    ds18s = db.query(DS18B20).all()
    scds = db.query(SCD41).all()

    results = normalize_measurements(dmis, bmes, ds18s, scds)

    # Filtrer efter type og tid
    if type_:
        results = [r for r in results if r["parameter"] == type_]
    if from_dt:
        results = [r for r in results if r["observed_at"] >= from_dt]
    if to_dt:
        results = [r for r in results if r["observed_at"] <= to_dt]

    return results