import os
import json
from math import radians, sin, cos, sqrt, atan2
from datetime import datetime, timedelta, timezone
from typing import List, Optional

import httpx
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi_mcp import FastApiMCP
from pydantic import BaseModel, Field

load_dotenv()
ORS_API_KEY = os.getenv("ORS_API_KEY")

app = FastAPI()

# -------------------- Models --------------------

class GeocodeRequest(BaseModel):
    location_text: str = Field(..., example="San Francisco, CA")

class GeocodeResponse(BaseModel):
    latitude: float
    longitude: float
    location_name: Optional[str]
    meta: Optional[dict]

class RouteRequest(BaseModel):
    coordinates: List[List[float]] = Field(
        ..., example=[[-122.4194, 37.7749], [-119.4179, 36.7783], [-118.2437, 34.0522]]
    )
    avoid_prefs: Optional[List[str]] = Field(None, example=["ferries", "tollways"])

class RouteSummary(BaseModel):
    distance_km: float
    duration_min: float
    estimated_arrival: str
    steps: List[str]
    start: List[float]
    end: List[float]

class MountainSearchRequest(BaseModel):
    lat: float = Field(..., example=37.7749)
    lon: float = Field(..., example=-122.4194)
    radius_m: int = Field(25000, example=25000)

class Peak(BaseModel):
    name: str
    lat: float
    lon: float

class EVChargerRequest(BaseModel):
    lat: float = Field(..., example=37.7749)
    lon: float = Field(..., example=-122.4194)
    radius_km: float = Field(50, example=50)

class EVChargerSite(BaseModel):
    name: str
    lat: float
    lon: float
    distance_km: float
    status: str

# -------------------- Geocoding --------------------

@app.post("/geocode_location", response_model=GeocodeResponse, operation_id="geocode_location", summary="Geocode a location string")
async def geocode_location(request: GeocodeRequest):
    location_text = request.location_text.strip().lower()
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                "https://nominatim.openstreetmap.org/search",
                params={"q": location_text, "format": "json", "limit": 1},
                headers={"User-Agent": "geocoding-tool"}
            )
        data = response.json()
        if not data:
            raise HTTPException(status_code=404, detail={"error": "LOCATION_NOT_FOUND", "message": "No matching location found."})

        result = data[0]
        return GeocodeResponse(
            latitude=float(result["lat"]),
            longitude=float(result["lon"]),
            location_name=result.get("display_name"),
            meta={
                "type": result.get("type"),
                "importance": result.get("importance")
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail={"error": "GEOCODING_FAILED", "message": str(e)})

# -------------------- Route --------------------

@app.post("/get_route", response_model=RouteSummary, operation_id="get_route", summary="Get driving route with summary")
async def get_route(request: RouteRequest):
    payload = {
        "coordinates": request.coordinates,
        "instructions": True
    }
    if request.avoid_prefs:
        payload["options"] = {"avoid_features": request.avoid_prefs}

    headers = {
        "Authorization": ORS_API_KEY,
        "Content-Type": "application/json"
    }

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://api.openrouteservice.org/v2/directions/driving-car/geojson",
                json=payload,
                headers=headers
            )
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail={"error": "ORS_API_FAILED", "message": response.text})

        geojson = response.json()
        features = geojson.get("features", [])
        if not features:
            raise HTTPException(status_code=500, detail={"error": "NO_ROUTE_FOUND", "message": "No route data available."})

        summary = features[0]["properties"]["summary"]
        steps = features[0]["properties"].get("segments", [])[0].get("steps", [])
        step_summaries = steps[:5] + steps[-5:] if len(steps) > 10 else steps
        directions = [step["instruction"] for step in step_summaries]

        eta = datetime.now(timezone.utc) + timedelta(minutes=summary["duration"] / 60)
        eta_str = eta.strftime("%Y-%m-%d %H:%M UTC")

        return RouteSummary(
            distance_km=round(summary["distance"] / 1000, 2),
            duration_min=round(summary["duration"] / 60, 2),
            estimated_arrival=eta_str,
            steps=directions,
            start=request.coordinates[0],
            end=request.coordinates[-1]
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail={"error": "ROUTE_ERROR", "message": str(e)})

# -------------------- Mountain Search --------------------

@app.post("/search_mountains", response_model=List[Peak], operation_id="search_mountains", summary="Search nearby mountain peaks")
async def search_mountains(request: MountainSearchRequest):
    query = f"""
    [out:json];
    node
      ["natural"="peak"]
      (around:{request.radius_m},{request.lat},{request.lon});
    out;
    """
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://overpass-api.de/api/interpreter",
                data=query.strip(),
                headers={"Content-Type": "application/x-www-form-urlencoded"}
            )
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail={"error": "OVERPASS_API_FAILED"})

        data = response.json()
        elements = data.get("elements", [])

        peaks = [
            Peak(
                name=el.get("tags", {}).get("name", "Unnamed Peak"),
                lat=el["lat"],
                lon=el["lon"]
            )
            for el in elements if "lat" in el and "lon" in el
        ]

        return peaks[:3]  # Return top 3

    except Exception as e:
        raise HTTPException(status_code=500, detail={"error": "MOUNTAIN_SEARCH_FAILED", "message": str(e)})

# -------------------- EV Chargers --------------------

# Load once into memory
with open("ev_chargers.json") as f:
    CHARGER_DATA = json.load(f)

def haversine(lat1, lon1, lat2, lon2):
    R = 6371  # Earth radius in km
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat / 2) ** 2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon / 2) ** 2
    return R * 2 * atan2(sqrt(a), sqrt(1 - a))

@app.post("/get_ev_chargers", response_model=List[EVChargerSite], operation_id="get_ev_chargers", summary="Get nearby EV chargers")
async def get_ev_chargers(req: EVChargerRequest):
    nearby = []
    for site in CHARGER_DATA:
        gps = site.get("gps", {})
        site_lat = gps.get("latitude")
        site_lon = gps.get("longitude")
        if site_lat is not None and site_lon is not None:
            dist = haversine(req.lat, req.lon, site_lat, site_lon)
            if dist <= req.radius_km:
                nearby.append(EVChargerSite(
                    name=site.get("name", "Unnamed Site"),
                    lat=site_lat,
                    lon=site_lon,
                    distance_km=round(dist, 2),
                    status=site.get("status", "unknown")
                ))
    return sorted(nearby, key=lambda x: x.distance_km)

# -------------------- MCP Mount --------------------

mcp = FastApiMCP(
    app,
    name="Route Planning MCP",
    description="MCP-compatible API for route planning, mountain search, geocoding, and EV charging."
)

mcp.mount()