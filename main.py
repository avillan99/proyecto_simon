import asyncio
import os
import re
from datetime import date, timedelta
from dotenv import load_dotenv
from playwright.async_api import async_playwright, TimeoutError as PWTimeoutError, expect

# Configuration
BASE_URL = "https://simon.inder.gov.co"
HEADLESS = False
SLOW_MO = 300  # milliseconds

# Get variables from .env
load_dotenv()
NUM_DOCUMENTO_PRINC = os.getenv("NUM_DOCUMENTO_PRINC", "")
LOGIN_PASSWORD = os.getenv("LOGIN_PASSWORD", "")
GUEST_NUMDOC = os.getenv("GUEST_NUMDOC", "")


def nearest_future_friday(d: date | None = None) -> date:
    d = d or date.today()
    days_ahead = (4 - d.weekday()) % 7  # Friday=4
    if days_ahead == 0:
        days_ahead = 7  # strictly future
    return d + timedelta(days=days_ahead)

async def launch_program(headless: bool = HEADLESS, slow_mo: int | None = SLOW_MO):
    # async with async_playwright() as p:
    p = await async_playwright().start()
    browser = await p.chromium.launch(headless=headless,slow_mo=slow_mo)
    context = await browser.new_context()
    page = await context.new_page()
    return page

async def go_to_login(page,base_url=BASE_URL):
    await page.goto(f"{base_url}/login/", wait_until="domcontentloaded")
    print("Page title:", await page.title())
    return page

# class PageNavigator:
#     def __init__(self, headless: bool = HEADLESS, slow_mo: int | None = SLOW_MO):
#         self.page = aw

async def main():
    async with async_playwright() as p:
        #Launch browser
        # browser = await p.chromium.launch(headless=False,slow_mo=300)
        # context = await browser.new_context()
        # page = await context.new_page()
        page = await launch_program()
        # Navigate to Simon's login page
        # await page.goto(f"{BASE_URL}/login/", wait_until="domcontentloaded")
        # #await page.wait_for_timeout(300)  # small "human-like" pause
        # print("Page title:", await page.title())

        page = await go_to_login(page)
        # Interact with the dropdown menu
        field = page.get_by_label("Tipo de documento")
        await field.click(timeout=10000)
        option = page.get_by_role("option", name="Cédula de Ciudadanía")
        await option.click(timeout=10000)
        # Fill in the document number and password fields
        locator = page.get_by_label(re.compile("n[uú]mero de documento", re.I))
        await locator.fill(NUM_DOCUMENTO_PRINC, timeout=10000)
        locator = page.get_by_label(re.compile("contraseñ?a", re.I))
        await locator.fill(LOGIN_PASSWORD, timeout=10000)
        # Click the login button
        login_button = page.get_by_role("button", name=re.compile("ingresar|entrar|login", re.I))
        await login_button.click(timeout=10000)
        #await page.wait_for_timeout(300)  # small "human-like" pause
        # Wait for post-login state: URL change or a known element (adjust as you observe)
        try:
            await page.wait_for_url(re.compile(r".*/(home|inicio|dashboard|scenarios|reservas).*", re.I), timeout=20000)
            #await page.wait_for_timeout(300)  # small "human-like" pause
        except PWTimeoutError:
            # fallback: just wait for some authenticated-only element
            await page.wait_for_timeout(5000)
        # Navigate through the menu to "Escenarios" > "Reservas"
        menu_labels = ["Escenarios", "Reservas"]
        for lab in menu_labels:
            link = page.get_by_text(re.compile(re.escape(lab), re.I))
            await link.click(timeout=10000)
            #await page.wait_for_timeout(300)  # small "human-like" pause

        # Fill out the reservation form
        ## Choose City
        field = page.get_by_role("combobox", name=re.compile("Municipio", re.I))
        await field.click(timeout=10000)
        #await page.wait_for_timeout(300)  # small "human-like" pause
        option = page.get_by_role("option", name=re.compile("Medellín", re.I))
        await option.click(timeout=10000)
        ## Choose Zone
        #await page.wait_for_timeout(300)  # small "human-like" pause
        field = page.get_by_role("combobox", name=re.compile("Zona", re.I))
        await field.click(timeout=10000)
        #await page.wait_for_timeout(300)  # small "human-like" pause
        option = page.get_by_role("option", name=re.compile("Urbana", re.I))
        await option.click(timeout=10000)
        #await page.wait_for_timeout(300)  # small "human-like" pause
        ## Choose Neighborhood
        field = page.get_by_role("combobox", name=re.compile("Barrio", re.I))
        await field.click(timeout=10000)
        #await page.wait_for_timeout(300)  # small "human-like" pause
        option = page.get_by_role("option", name=re.compile("Rosales", re.I))
        await option.click(timeout=10000)
        #await page.wait_for_timeout(300)  # small "human-like" pause
        ## Choose Scenario Type
        field = page.get_by_role("combobox", name=re.compile("Tipo de Escenario", re.I))
        await field.click(timeout=10000)
        #await page.wait_for_timeout(300)  # small "human-like" pause
        option = page.get_by_role("option", name=re.compile("Tenis", re.I))
        await option.click(timeout=10000)
        #await page.wait_for_timeout(300)  # small "human-like" pause
        ## Choose Unit Type
        field = page.get_by_role("combobox", name=re.compile("Tipo de Unidad", re.I))
        await field.click(timeout=10000)
        #await page.wait_for_timeout(300)  # small "human-like" pause
        option = page.get_by_role("option", name=re.compile("Unidad deportiva", re.I))
        await option.click(timeout=10000)
        #await page.wait_for_timeout(300)  # small "human-like" pause

        # Select the scenario and click "Reservar"
        scenario_row = page.get_by_role("row").filter(has=page.get_by_text("Belén Andrés", exact=False)
                                                      ).filter(has=page.get_by_text("campo N 3", exact=False))
        await scenario_row.locator('[data-field="ACTIONS"] button').click()
        #await page.wait_for_timeout(300)  # small "human-like" pause
        await page.get_by_role("menuitem", name="Reservar").click()
        #await page.wait_for_timeout(300)  # small "human-like" pause

        # Select division to reserve
        await page.get_by_label("Selecciona la división a reservar *").click()
        #await page.wait_for_timeout(300)  # small "human-like" pause
        await page.get_by_role("option", name="Completa").click()
        #await page.wait_for_timeout(300)  # small "human-like" pause
        await page.get_by_role("listbox").wait_for(state="hidden")
        #await page.wait_for_timeout(300)  # small "human-like" pause

        # wait for calendar
        await expect(page.locator(".fc")).to_be_visible(timeout=15000)
        next_btn = page.locator("button.fc-next-button")
        target = nearest_future_friday()  # first candidate Friday (future)
        max_weeks_to_try = 2            # adjust as you like
        for _ in range(max_weeks_to_try):
            friday_str = target.isoformat()  # YYYY-MM-DD
            friday_col = page.locator(f'.fc-timegrid-col[data-date="{friday_str}"]')

            # Ensure the target Friday is visible: click Next week until its column exists
            for _ in range(1):  # should only need a few clicks
                if await friday_col.count():
                    break
                await expect(next_btn).to_be_visible(timeout=15000)
                await next_btn.click()
                #await page.wait_for_timeout(300)  # small "human-like" pause

            # If still not visible, jump to next week candidate
            if not await friday_col.count():
                target = target + timedelta(days=7)
                continue

            # Look for the available 8–9 slot in that Friday column
            slot = friday_col.locator(".fc-timegrid-event").filter(
                has=page.get_by_text("08:00 PM - 09:00 PM", exact=False)
            ).filter(
                has=page.get_by_text("Bloque Disponible", exact=False)
            )

            if await slot.count():
                await slot.first.click()
                #await page.wait_for_timeout(300)  # small "human-like" pause
                break  # ✅ found the nearest available Friday
            else:
                # Not available that Friday → try next Friday
                target = target + timedelta(days=7)
        else:
            raise RuntimeError("No available Friday 8–9 PM slot found in the next weeks.")

        #
        add_info_btn = page.get_by_role("button", name=re.compile("Agregar información adicional", re.I))
        await expect(add_info_btn).to_be_visible(timeout=15000)
        await add_info_btn.click()
        add_info_btn_2 = page.get_by_role("button", name=re.compile("Agregar informacion", re.I))
        await expect(add_info_btn_2).to_be_visible(timeout=15000)
        await add_info_btn_2.click()

        add_participant_btn = page.get_by_role("button", name=re.compile("Agregar Participantes", re.I))
        await add_participant_btn.click()
        # dialog = page.get_by_role("dialog", name="Participantes")
        field = page.get_by_label("Tipo de documento")
        await field.click(timeout=10000)
        option = page.get_by_role("option", name="Cédula de Ciudadanía")
        await option.click(timeout=10000)
        locator = page.get_by_label(re.compile("n[uú]mero de documento", re.I))
        await locator.fill(GUEST_NUMDOC, timeout=10000)
        login_button = page.get_by_role("button", name=re.compile("Buscar", re.I))
        await login_button.click(timeout=10000)
        add_info_btn = page.get_by_role("button", name=re.compile("Agregar información adicional", re.I))
        await expect(add_info_btn).to_be_visible(timeout=15000)
        await add_info_btn.click()
        add_info_btn_2 = page.get_by_role("button", name=re.compile("Agregar informacion", re.I))
        await expect(add_info_btn_2).to_be_visible(timeout=15000)
        await add_info_btn_2.click()
        save_bttn = page.get_by_role("button", name=re.compile("Guardar", re.I))
        await save_bttn.click(timeout=10000)
        reminder = page.get_by_role("dialog", name="Recuerda")
        await expect(reminder).to_be_visible(timeout=15000)
        await reminder.get_by_role("button", name="Aceptar").click()
        save_bttn_2 = page.get_by_role("button", name="Guardar")
        await save_bttn_2.click()
        # Close browser
        await page.wait_for_timeout(5000)  # small "human-like" pause
        await browser.close()

asyncio.run(main())