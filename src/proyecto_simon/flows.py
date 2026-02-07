from playwright.async_api import async_playwright

from .utils.calendar import generate_availability_html
from .config import load_settings
from .simon.api import client
from .simon.auth.login import ui_login, get_api_token
from .simon.browser import navigation as ui

DEFAULT_SETTINGS = load_settings()

async def reserve() -> None:
    async with async_playwright() as p:
        #Login
        page = await ui_login(pw_object=p)
        # Navigate to reserves
        await ui.go_to_reserves(page)
        # Fill reservation form
        await ui.fill_reservation_form(page, selections=DEFAULT_SETTINGS.scenario_filters)
        # Select the scenario and click "Reservar"
        await ui.select_scenario(page, *DEFAULT_SETTINGS.scenario_keywords)
        # Select division to reserve
        await ui.select_division(page, division_name=DEFAULT_SETTINGS.division_name)
        # Select time slot
        await ui.select_time_slot(page,max_weeks_to_try=DEFAULT_SETTINGS.weeks_to_try,desired_time_slot=DEFAULT_SETTINGS.desired_time_slot)
        # Host Info prepared. Confirm it.
        await ui.confirm_participant_info(page,participant_numdoc=DEFAULT_SETTINGS.num_documento_princ)
        # Other participants
        await ui.add_participant(page, guest_numdoc=DEFAULT_SETTINGS.guest_numdoc)
        # Save reservation
        await ui.save_reservation(page)
        print("✅ Reservation flow completed (verify in UI).")
        await page.wait_for_timeout(10000)  # small "human-like" pause


async def generate_availability(division_pk_list: list[int]) -> None:
    async with async_playwright() as p:
        # Capture bearer token
        token = await get_api_token(pw_object=p)
        # Consult data for every division_pk
        data = await client.massive_get_division_data(token=token, division_pks=division_pk_list)
        # Process and combine data as needed for analysis or output
        generate_availability_html(data)
        print("✅ Availability generation flow completed.")