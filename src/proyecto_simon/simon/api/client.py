import httpx

from proyecto_simon.constants.urls import API_BASE_URL, BASE_URL

#Estadio
## Cancha 10: 293
## Cancha 8: 309
## Cancha 9: 311

DIVISION_PK = 293

import httpx

async def get_division_data(token: str, division_pk: int) -> dict:
    headers = {
        "accept": "application/json",
        "authorization": f"bearer {token}",
        "origin": f"{BASE_URL}",
        "referer": f"{BASE_URL}/",
        "user-agent": "Mozilla/5.0",
    }

    async with httpx.AsyncClient(base_url=API_BASE_URL, timeout=30) as client:
        r = await client.get(f"/api/scenarios-booking/divisions/{division_pk}/", headers=headers)
        print("STATUS:", r.status_code, "CT:", r.headers.get("content-type"))
        print("SNIP:", r.text[:120])
        r.raise_for_status()
        return r.json()

