from dataclasses import dataclass, field
import os

from dotenv import load_dotenv

from .constants.urls import BASE_URL
from .validations import verify_env_inputs

@dataclass()
class Settings:
    base_url: str = BASE_URL
    headless: bool = False
    slow_mo_ms: int = 300

    scenario_filters: dict[str, str] = field(default_factory= lambda: {
        "Municipio": "Medellín",
        "Zona": "Urbana",
        "Barrio": "Rosales",
        "Tipo de Escenario": "Tenis",
        "Tipo de Unidad": "Unidad deportiva",
    })
    scenario_keywords: tuple[str, ...] = ("Belén Andrés", "campo N 3")

    division_name: str = "Completa"
    weeks_to_try: int = 3
    desired_time_slot: str = "08:00 PM - 09:00 PM"

    num_documento_princ: str = ""
    login_password: str = ""
    guest_numdoc: str = ""

def load_settings() -> Settings:
    load_dotenv()
    num_documento_princ = os.getenv("NUM_DOCUMENTO_PRINC", "")
    login_password = os.getenv("LOGIN_PASSWORD", "")
    guest_numdoc = os.getenv("GUEST_NUMDOC", "")

    verify_env_inputs(num_documento_princ, login_password, guest_numdoc)
    
    return Settings(
        num_documento_princ=num_documento_princ,
        login_password=login_password,
        guest_numdoc=guest_numdoc,
    )