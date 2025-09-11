import json
import math
import random
from typing import Tuple, List

from geopy.distance import geodesic


class LGPoint:
    def __init__(self, longitude: float, latitude: float):
        self.longitude = longitude
        self.latitude = latitude

    def __repr__(self):
        return f"LGPoint(lon={self.longitude:.6f}, lat={self.latitude:.6f})"
    #需要时可以被json序列化的
    def to_dict(self):
        return {"longitude": self.longitude, "latitude": self.latitude}

# WGS-84 转 GCJ-02
def wgs84_to_gcj02(lat: float, lon: float) -> Tuple[float, float]:
    A = 6378245.0
    EE = 0.006693421622965943

    def out_of_china(lat, lon):
        return not (72.004 <= lon <= 137.8347 and 0.8293 <= lat <= 55.8271)

    def transform_lat(x, y):
        ret = -100.0 + 2.0 * x + 3.0 * y + 0.2 * y * y + 0.1 * x * y + math.sqrt(abs(x)) * 0.2
        ret += (20.0 * math.sin(6.0 * x * math.pi) + 20.0 * math.sin(2.0 * x * math.pi)) * 2.0 / 3.0
        ret += (20.0 * math.sin(y * math.pi) + 40.0 * math.sin(y / 3.0 * math.pi)) * 2.0 / 3.0
        ret += (160.0 * math.sin(y / 12.0 * math.pi) + 320.0 * math.sin(y * math.pi / 30.0)) * 2.0 / 3.0
        return ret

    def transform_lon(x, y):
        ret = 300.0 + x + 2.0 * y + 0.1 * x * x + 0.1 * x * y + math.sqrt(abs(x)) * 0.1
        ret += (20.0 * math.sin(6.0 * x * math.pi) + 20.0 * math.sin(2.0 * x * math.pi)) * 2.0 / 3.0
        ret += (20.0 * math.sin(x * math.pi) + 40.0 * math.sin(x / 3.0 * math.pi)) * 2.0 / 3.0
        ret += (150.0 * math.sin(x / 12.0 * math.pi) + 300.0 * math.sin(x / 30.0 * math.pi)) * 2.0 / 3.0
        return ret

    if out_of_china(lat, lon):
        return lat, lon

    d_lat = transform_lat(lon - 105.0, lat - 35.0)
    d_lon = transform_lon(lon - 105.0, lat - 35.0)
    rad_lat = lat / 180.0 * math.pi
    magic = math.sqrt(1 - EE * math.sin(rad_lat) ** 2)
    d_lat = (d_lat * 180.0) / ((A * (1 - EE)) / (magic * magic) * math.pi)
    d_lon = (d_lon * 180.0) / (A / magic * math.cos(rad_lat) * math.pi)
    mg_lat = lat + d_lat
    mg_lon = lon + d_lon
    return mg_lat, mg_lon

def get_routine(mileage: float, geojson_str: str) -> List[LGPoint]:
    geo_json = json.loads(geojson_str)

    features = geo_json.get("features")
    if not features:
        raise ValueError("No feature found")

    geometry = features[0].get("geometry")
    if not geometry or geometry["type"] != "LineString":
        raise ValueError("Invalid geometry")

    coordinates = geometry["coordinates"]
    if not coordinates:
        raise ValueError("No coordinates found")

    points = []
    last = None

    while True:
        for lon, lat in coordinates:
            y, x = wgs84_to_gcj02(lat, lon)  # 注意：Rust 里 (lat, lon)，Python 也保持一致

            if last is None:
                last = (y, x)

            # 随机扰动
            new_lon = x + random.uniform(-5e-6, 5e-6)
            new_lat = y + random.uniform(-5e-6, 5e-6)

            # 距离（km）
            mileage -= geodesic((last[0], last[1]), (y, x)).meters / 1000.0
            last = (y, x)

            points.append(LGPoint(new_lon, new_lat))

            if mileage <= 0:
                return points
