from playwright.async_api import async_playwright, Playwright

from proyecto_simon.config import load_settings
from proyecto_simon.simon.browser import navigation as ui
from .token import capture_bearer_token

DEFAULT_SETTINGS = load_settings()

async def ui_login(pw_object: Playwright):
    #Launch browser
    page = await ui.launch_program(pw_object = pw_object, headless=True, slow_mo=0)
    #Login
    await ui.go_to_login(page)
    await ui.login(page, num_documento = DEFAULT_SETTINGS.num_documento_princ, password = DEFAULT_SETTINGS.login_password)
    await ui.wait_for_post_login(page)
    return page

async def get_api_token(pw_object: Playwright) -> str:
    #Login
    page = await ui_login(pw_object)
    # Capture bearer token
    token = await capture_bearer_token(page)
    print("TOKEN FOUND:", token[:20], "...")
    # Consult data for every division_pk
    return token