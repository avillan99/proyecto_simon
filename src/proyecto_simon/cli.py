import asyncio
import re
from datetime import date, timedelta

from playwright.async_api import Playwright,async_playwright, TimeoutError as PWTimeoutError, expect

from .config import load_settings
DEFAULT_SETTINGS = load_settings()
BASE_URL = DEFAULT_SETTINGS.base_url

def nearest_future_friday(d: date | None = None) -> date:
    d = d or date.today()
    days_ahead = (4 - d.weekday()) % 7  # Friday=4
    if days_ahead == 0:
        days_ahead = 7  # strictly future
    return d + timedelta(days=days_ahead)

async def launch_program(pw_object: Playwright, headless: bool, slow_mo: int):
    browser = await pw_object.chromium.launch(headless=headless,slow_mo=slow_mo)
    context = await browser.new_context()
    page = await context.new_page()
    return page

async def go_to_login(page):
    await page.goto(f"{BASE_URL}/login/", wait_until="domcontentloaded")
    print("Page title:", await page.title())

async def login(page, num_documento: str, password: str):
    # Interact with the dropdown menu
    field = page.get_by_label("Tipo de documento")
    await field.click(timeout=10000)
    option = page.get_by_role("option", name="Cédula de Ciudadanía")
    await option.click(timeout=10000)
    # Fill in the document number and password fields
    locator = page.get_by_label(re.compile("n[uú]mero de documento", re.I))
    await locator.fill(num_documento, timeout=10000)
    locator = page.get_by_label(re.compile("contraseñ?a", re.I))
    await locator.fill(password, timeout=10000)
    # Click the login button
    login_button = page.get_by_role("button", name=re.compile("ingresar|entrar|login", re.I))
    await login_button.click(timeout=10000)

async def wait_for_post_login(page):
    # Wait for post-login state: URL change or a known element (adjust as you observe)
    try:
        # await page.wait_for_url(re.compile(r".*/(home|inicio|dashboard|scenarios|reservas).*", re.I), timeout=20000)
        await page.wait_for_url(re.compile(r".*/dashboards.*", re.I), timeout=20000)
    except PWTimeoutError:
        # fallback: just wait for some authenticated-only element
        await page.wait_for_timeout(5000)

async def go_to_reserves(page):
    # Navigate through the menu to "Escenarios" > "Reservas"
    menu_labels = ["Escenarios", "Reservas"]
    for lab in menu_labels:
        link = page.get_by_text(re.compile(re.escape(lab), re.I))
        await link.click(timeout=10000)

async def fill_reservation_form(page, selections: dict[str, str]):
    # Fill out the reservation form with the specified selections

    for field_label, option_text in selections.items():
        field = page.get_by_role("combobox", name=re.compile(field_label, re.I))
        await field.click(timeout=10000)
        option = page.get_by_role("option", name=re.compile(option_text, re.I))
        await option.click(timeout=10000)

async def select_scenario(page, *scenario_keywords: str):
    """Select a scenario row by applying one or more keyword filters.

    Each keyword is applied as an additional `.filter(has=page.get_by_text(...))` call
    so all keywords must match the same row. Example:
        await select_scenario(page, "Belén Andrés", "campo N 3")
    """
    selector = page.get_by_role("row")
    for kw in scenario_keywords:
        selector = selector.filter(has=page.get_by_text(kw, exact=False))
    await selector.locator('[data-field="ACTIONS"] button').click()
    # small "human-like" pause could be added if desired
    await page.get_by_role("menuitem", name="Reservar").click()

async def select_division(page, division_name: str):
    division_field = page.get_by_label("Selecciona la división a reservar *")
    await division_field.click(timeout=10000)
    division_option = page.get_by_role("option", name=division_name)
    await division_option.click(timeout=10000)
    await page.get_by_role("listbox").wait_for(state="hidden")

async def select_time_slot(page,max_weeks_to_try: int,desired_time_slot: str ):

    # wait for calendar
    await expect(page.locator(".fc")).to_be_visible(timeout=15000)
    next_btn = page.locator("button.fc-next-button")
    target = nearest_future_friday()  # first candidate Friday (future)
    for _ in range(max_weeks_to_try):
        friday_str = target.isoformat()  # YYYY-MM-DD
        friday_col = page.locator(f'.fc-timegrid-col[data-date="{friday_str}"]')

        # Ensure the target Friday is visible: click Next week until its column exists
        for _ in range(1):  # should only need a few clicks
            if await friday_col.count():
                break
            await expect(next_btn).to_be_visible(timeout=15000)
            await next_btn.click()

        # If still not visible, jump to next week candidate
        if not await friday_col.count():
            target = target + timedelta(days=7)
            continue

        # Look for the available 8–9 slot in that Friday column
        slot = friday_col.locator(".fc-timegrid-event").filter(
            has=page.get_by_text(desired_time_slot, exact=False)
        ).filter(
            has=page.get_by_text("Bloque Disponible", exact=False)
        )

        if await slot.count():
            await slot.first.click()
            break  # ✅ found the nearest available Friday
        else:
            # Not available that Friday → try next Friday
            target = target + timedelta(days=7)
    else:
        raise RuntimeError("No available slot found in the next weeks.")

async def confirm_participant_info(page):
    add_info_btn = page.get_by_role("button", name=re.compile("Agregar información adicional", re.I))
    await expect(add_info_btn).to_be_visible(timeout=15000)
    await add_info_btn.click()
    add_info_btn_2 = page.get_by_role("button", name=re.compile("Agregar informacion", re.I))
    await expect(add_info_btn_2).to_be_visible(timeout=15000)
    await add_info_btn_2.click()

async def add_participant(page, guest_numdoc: str):
    add_participant_btn = page.get_by_role("button", name=re.compile("Agregar Participantes", re.I))
    await add_participant_btn.click()
    field = page.get_by_label("Tipo de documento")
    await field.click(timeout=10000)
    option = page.get_by_role("option", name="Cédula de Ciudadanía")
    await option.click(timeout=10000)
    locator = page.get_by_label(re.compile("n[uú]mero de documento", re.I))
    await locator.fill(guest_numdoc, timeout=10000)
    login_button = page.get_by_role("button", name=re.compile("Buscar", re.I))
    await login_button.click(timeout=10000)
    await confirm_participant_info(page)

async def save_reservation(page):
    save_bttn = page.get_by_role("button", name=re.compile("Guardar", re.I))
    await save_bttn.click(timeout=10000)
    reminder = page.get_by_role("dialog", name="Recuerda")
    await expect(reminder).to_be_visible(timeout=15000)
    await reminder.get_by_role("button", name="Aceptar").click()
    save_bttn_2 = page.get_by_role("button", name="Guardar")
    await save_bttn_2.click()

async def main() -> None:
    async with async_playwright() as p:
        #Launch browser
        page = await launch_program(pw_object = p, headless=DEFAULT_SETTINGS.headless, slow_mo=DEFAULT_SETTINGS.slow_mo_ms)
        #Login
        await go_to_login(page)
        await login(page, num_documento = DEFAULT_SETTINGS.num_documento_princ, password = DEFAULT_SETTINGS.login_password)
        await wait_for_post_login(page)
        # Navigate to reserves
        await go_to_reserves(page)
        # Fill reservation form
        await fill_reservation_form(page, selections=DEFAULT_SETTINGS.scenario_filters)
        # Select the scenario and click "Reservar"
        await select_scenario(page, *DEFAULT_SETTINGS.scenario_keywords)
        # Select division to reserve
        await select_division(page, division_name=DEFAULT_SETTINGS.division_name)
        # Select time slot
        await select_time_slot(page,max_weeks_to_try=DEFAULT_SETTINGS.weeks_to_try,desired_time_slot=DEFAULT_SETTINGS.desired_time_slot)
        # Host Info prepared. Confirm it.
        await confirm_participant_info(page)
        # Other participants
        await add_participant(page, guest_numdoc=DEFAULT_SETTINGS.guest_numdoc)
        # Save reservation
        await save_reservation(page)
        print("✅ Reservation flow completed (verify in UI).")
        await page.wait_for_timeout(10000)  # small "human-like" pause

if __name__ == "__main__":
    asyncio.run(main())