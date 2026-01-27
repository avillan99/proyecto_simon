import asyncio

from playwright.async_api import async_playwright

from .config import load_settings
from . import ui_actions as ui

DEFAULT_SETTINGS = load_settings()
BASE_URL = DEFAULT_SETTINGS.base_url

async def main() -> None:
    async with async_playwright() as p:
        #Launch browser
        page = await ui.launch_program(pw_object = p, headless=DEFAULT_SETTINGS.headless, slow_mo=DEFAULT_SETTINGS.slow_mo_ms)
        #Login
        await ui.go_to_login(page)
        await ui.login(page, num_documento = DEFAULT_SETTINGS.num_documento_princ, password = DEFAULT_SETTINGS.login_password)
        await ui.wait_for_post_login(page)
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

if __name__ == "__main__":
    asyncio.run(main())