import pytest
from map.services.hospital_service import haversine_km

def test_haversine_km_same_point():
    assert haversine_km(30.0, 31.0, 30.0, 31.0) == 0.0

def test_haversine_km_known_distance():
    # Cairo (30.0444, 31.2357) to Alex (31.2001, 29.9187) is ~180 km
    dist = haversine_km(30.0444, 31.2357, 31.2001, 29.9187)
    assert 170 < dist < 190

def test_haversine_km_symmetry():
    d1 = haversine_km(30.0, 31.0, 31.0, 30.0)
    d2 = haversine_km(31.0, 30.0, 30.0, 31.0)
    assert d1 == d2

