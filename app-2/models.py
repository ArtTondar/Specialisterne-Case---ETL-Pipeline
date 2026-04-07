from sqlalchemy import Column, Float, Integer, String, Numeric, TIMESTAMP, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class DMI(Base):
    __tablename__ = "DMI"
    DMI_id = Column(Integer, primary_key=True, index=True)
    dmi_id = Column(UUID(as_uuid=True), nullable=False)
    parameter_id = Column(String(50), nullable=False)  # temperature, humidity, pressure
    value = Column(Float, nullable=False)
    observed_at = Column(TIMESTAMP(timezone=True), nullable=False)
    pulled_at = Column(TIMESTAMP(timezone=True), nullable=False)
    station_id = Column(Integer, nullable=False)


class BME280(Base):
    __tablename__ = "BME280"
    BME280_id = Column(Integer, primary_key=True, index=True)
    reader_id = Column(UUID(as_uuid=True), nullable=False)
    location = Column(String(7), nullable=False)  # inside / outside
    temperature = Column(Numeric(20, 13))
    humidity = Column(Numeric(20, 13))
    pressure = Column(Numeric(20, 13))
    observed_at = Column(TIMESTAMP(timezone=True), nullable=False)
    pulled_at = Column(TIMESTAMP(timezone=True), nullable=False)


class DS18B20(Base):
    __tablename__ = "DS18B20"
    DS18B20_id = Column(Integer, primary_key=True, index=True)
    reader_id = Column(UUID(as_uuid=True), nullable=False)
    location = Column(String(7), nullable=False)  # inside / outside
    temperature = Column(Numeric(20, 13))
    observed_at = Column(TIMESTAMP(timezone=True), nullable=False)
    pulled_at = Column(TIMESTAMP(timezone=True), nullable=False)


class SCD41(Base):
    __tablename__ = "SCD41"
    SCD41_id = Column(Integer, primary_key=True, index=True)
    reader_id = Column(UUID(as_uuid=True), nullable=False)
    co2 = Column(Integer)
    temperature = Column(Numeric(20, 13))
    humidity = Column(Numeric(20, 13))
    observed_at = Column(TIMESTAMP(timezone=True), nullable=False)
    pulled_at = Column(TIMESTAMP(timezone=True), nullable=False)