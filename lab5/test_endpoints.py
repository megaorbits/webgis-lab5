import json
import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "webgis.settings")
django.setup()

from django.test import Client
from districts.models import District
from facilities.models import Facility

client = Client()

print("--- 1. Django Models Check ---")
print(f"Districts: {District.objects.count()}")
print(f"Facilities: {Facility.objects.count()}")

print("\n--- 2. Map Page GET / ---")
r_map = client.get("/")
print(f"Status: {r_map.status_code}")
content = r_map.content.decode("utf-8")
print(f"Contains DISTRICTS_URL: {'const DISTRICTS_URL = \"/api/districts/\";' in content}")
print(f"Contains FACILITIES_URL: {'const FACILITIES_URL = \"/api/facilities/\";' in content}")
print(f"Contains CSRF_TOKEN: {'const CSRF_TOKEN = \"' in content}")

print("\n--- 3. API Root GET /api/ ---")
r_api = client.get("/api/")
print(f"Status: {r_api.status_code}")
print(f"Content: {r_api.content.decode('utf-8')[:150]}")

print("\n--- 4. Districts API GET /api/districts/?format=json ---")
r_dist = client.get("/api/districts/?format=json")
print(f"Status: {r_dist.status_code}")
dist_data = json.loads(r_dist.content)
print(f"Districts count: {len(dist_data['features'])}, total size: {len(r_dist.content)} bytes ({round(len(r_dist.content)/1024)} KB)")

print("\n--- 5. Districts BBox Filter (Lahore) ---")
r_bbox = client.get("/api/districts/?in_bbox=74.0,31.2,74.7,31.8&format=json")
bbox_data = json.loads(r_bbox.content)
names = [f["properties"]["name"] for f in bbox_data["features"]]
print(f"Status: {r_bbox.status_code}, Count: {len(bbox_data['features'])}, Names: {names}")

print("\n--- 6. Districts Province Filter (Sindh) ---")
r_sindh = client.get("/api/districts/?province=Sindh&format=json")
sindh_data = json.loads(r_sindh.content)
print(f"Status: {r_sindh.status_code}, Sindh Districts Count: {len(sindh_data['features'])}")

print("\n--- 7. Facilities API GET /api/facilities/?format=json ---")
r_fac = client.get("/api/facilities/?format=json")
fac_data = json.loads(r_fac.content)
print(f"Status: {r_fac.status_code}, Facilities Count: {len(fac_data['features'])}")
for f in fac_data["features"]:
    print(f" - {f['properties']['name']} ({f['properties']['kind']}): district={f['properties']['district']}, coords={f['geometry']['coordinates']}")

print("\n--- 8. Facility 25km Distance Filter ---")
r_near = client.get("/api/facilities/?dist=25000&point=72.9906,33.6423&format=json")
near_data = json.loads(r_near.content)
print(f"Status: {r_near.status_code}, Nearby Count: {len(near_data['features'])}")
for f in near_data["features"]:
    print(f" - {f['properties']['name']}")

print("\n--- 9. Disallowed HTTP Methods (DELETE, PUT) ---")
first_fac_id = fac_data["features"][0]["id"]
r_del = client.delete(f"/api/facilities/{first_fac_id}/")
r_put = client.put(f"/api/facilities/{first_fac_id}/", data="{}", content_type="application/json")
print(f"DELETE status: {r_del.status_code} (Expected 405)")
print(f"PUT status: {r_put.status_code} (Expected 405)")

print("\n--- 10. Validation Tests ---")
# Sea test
r_sea = client.post("/api/facilities/", data=json.dumps({
    "type": "Feature",
    "geometry": {"type": "Point", "coordinates": [64.0, 23.0]},
    "properties": {"name": "Sea Test", "kind": "water"}
}), content_type="application/json")
print(f"Sea Point: {r_sea.status_code} -> {r_sea.content.decode('utf-8')}")

# Invalid kind
r_kind = client.post("/api/facilities/", data=json.dumps({
    "type": "Feature",
    "geometry": {"type": "Point", "coordinates": [72.9906, 33.6423]},
    "properties": {"name": "Castle Test", "kind": "castle"}
}), content_type="application/json")
print(f"Castle Kind: {r_kind.status_code} -> {r_kind.content.decode('utf-8')}")

# Swapped coordinates
r_swap = client.post("/api/facilities/", data=json.dumps({
    "type": "Feature",
    "geometry": {"type": "Point", "coordinates": [33.6423, 72.9906]},
    "properties": {"name": "Swapped Test", "kind": "school"}
}), content_type="application/json")
print(f"Swapped Coords: {r_swap.status_code} -> {r_swap.content.decode('utf-8')}")

