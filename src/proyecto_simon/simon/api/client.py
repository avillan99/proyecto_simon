import httpx

from proyecto_simon.constants.urls import API_BASE_URL, BASE_URL

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

async def massive_get_division_data(token: str, division_pks: list[int]) -> dict:
    data = {}
    for division_pk in division_pks:
        print("Consulting data for division_pk =", division_pk)
        data[division_pk] = await get_division_data(token=token, division_pk=division_pk)
        # breakpoint()
        # print(data)
        print("Scenary detail:", data[division_pk]["detail"])
        print("Timeslots by week: ",len(data[division_pk]["schedules"]))
        print("Sample: ", data[division_pk]["schedules"][:1])
        print("Found Bookings: ",len(data[division_pk]["bookings"]))
        print("Sample: ", data[division_pk]["bookings"][:1])
        print("✅ Consultation for division_pk =", division_pk, "completed.")
    return data