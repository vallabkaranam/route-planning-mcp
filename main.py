import os
from typing import List, Optional
from fastapi import FastAPI, HTTPException
import httpx
from pydantic import BaseModel, Field
from fastapi_mcp import FastApiMCP
from dotenv import load_dotenv
from datetime import datetime, timedelta, timezone
import json
from math import radians, sin, cos, sqrt, atan2

load_dotenv()
ORS_API_KEY = os.getenv("ORS_API_KEY")

app = FastAPI()

class GeocodeRequest(BaseModel):
    location_text: str = Field(
        ...,
        example="San Francisco, CA"
    )

class RouteRequest(BaseModel):
    coordinates: List[List[float]] = Field(
        ...,
        example=[[-122.4194, 37.7749], [-119.4179, 36.7783], [-118.2437, 34.0522]]
    )
    avoid_prefs: Optional[List[str]] = Field(
        None,
        example=["ferries", "tollways"]
    )

class MountainSearchRequest(BaseModel):
    lat: float = Field(..., example=37.7749)
    lon: float = Field(..., example=-122.4194)
    radius_m: int = Field(25000, example=25000)

class EVChargerRequest(BaseModel):
    lat: float = Field(..., example=37.7749)
    lon: float = Field(..., example=-122.4194)
    radius_km: float = Field(50, example=50)

@app.post("/geocode_location", operation_id="geocode_location")
async def geocode_location(request: GeocodeRequest):
    location_text = request.location_text.strip().lower()
    print(f"called with: {location_text}")

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                "https://nominatim.openstreetmap.org/search",
                params={"q": location_text, "format": "json", "limit": 1},
                headers={"User-Agent": "geocoding-tool"}
            )
            data = response.json()

        if not data:
            raise HTTPException(status_code=404, detail="Location not found.")

        result = data[0]
        return {
            "latitude": float(result["lat"]),
            "longitude": float(result["lon"]),
            "location_name": result.get("display_name"),
            "meta": {
                "type": result.get("type"),
                "importance": result.get("importance")
            }
        }

    except HTTPException as e:
        raise HTTPException(
            status_code=500,
            detail=f"HTTP error during geocoding: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error geocoding '{location_text}': {str(e)}"
        )

@app.post("/get_route", operation_id="get_route")
async def get_route(request: RouteRequest):
    payload = {
        "coordinates": request.coordinates,
        "instructions": True
    }

    if request.avoid_prefs:
        payload["options"] = {
            "avoid_features": request.avoid_prefs
        }

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
            raise HTTPException(
                status_code=response.status_code,
                detail=f"ORS error: {response.text}"
            )

        geojson = response.json()
        features = geojson.get("features", [])
        if features:
            summary = features[0]["properties"]["summary"]
            steps = features[0]["properties"].get("segments", [])[0].get("steps", [])
                    # Smart step slicing: first 3 + last 2
            if len(steps) > 10:
                step_summaries = steps[:5] + steps[-5:]
            else:
                step_summaries = steps

            directions = [step["instruction"] for step in step_summaries]


            eta = datetime.now(timezone.utc) + timedelta(minutes=summary["duration"] / 60)
            eta_str = eta.strftime("%Y-%m-%d %H:%M UTC")

            return {
                "distance_km": round(summary["distance"] / 1000, 2),
                "duration_min": round(summary["duration"] / 60, 2),
                "estimated_arrival": eta_str,
                "steps": directions,
                "start": request.coordinates[0],
                "end": request.coordinates[-1]
                # "geojson": geojson  # Optional, or remove for token savings
            }
        else:
            raise HTTPException(status_code=500, detail="No route found.")
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error getting route: {str(e)}"
        )

@app.post("/search_mountains", operation_id="search_mountains")
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
            raise HTTPException(status_code=response.status_code, detail="Overpass API error")

        data = response.json()
        elements = data.get("elements", [])

        peaks = [
            {
                "name": el.get("tags", {}).get("name", "Unnamed Peak"),
                "lat": el["lat"],
                "lon": el["lon"]
            }
            for el in elements if "lat" in el and "lon" in el
        ]

        return peaks[:3]  # Return top 3

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error searching mountains: {str(e)}")

# Load once into memory
with open("ev_chargers.json") as f:
    CHARGER_DATA = json.load(f)

def haversine(lat1, lon1, lat2, lon2):
    R = 6371  # Earth radius in km
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat / 2)**2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    return R * c

@app.post("/get_ev_chargers", operation_id="get_ev_chargers")
async def get_ev_chargers(req: EVChargerRequest):
    nearby = []
    for site in CHARGER_DATA:
        site_lat = site.get("gps", {}).get("latitude")
        site_lon = site.get("gps", {}).get("longitude")

        if site_lat is not None and site_lon is not None:
            dist = haversine(req.lat, req.lon, site_lat, site_lon)
            if dist <= req.radius_km:
                nearby.append({
                    "name": site.get("name"),
                    "lat": site_lat,
                    "lon": site_lon,
                    "distance_km": round(dist, 2),
                    "status": site.get("status", "unknown")
                })

    return sorted(nearby, key=lambda x: x["distance_km"])

mcp = FastApiMCP(
    app,
    name="Route Planning MCP",
    description="Simple API exposing route planning operations",
)

mcp.mount()