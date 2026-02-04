# Proyecto Automatización Plataforma INDER SIMON 2.0

Automatización del proceso de gestión (Reservas, Seguimientos, Cancelaciones) de escenarios deportivos para usuarios de la Plataforma SIMON (INDER / Alcaldía de Medellín).

## ¿Qué hace este proyecto?
- Reserva cancha de Tenis desde mi usuario específico, busca el escenario con los requerimientos especificados y agrega un invitado. 

## Configuración de Desarrollo

Este proyecto usa una capa src y está diseñado para ser instalado en modo editable mientras se desarrolla.

1. Clonar el repositorio:
   ```bash
   git clone https://github.com/youruser/proyecto_simon.git
   cd proyecto_simon

2. Crear y activar el venv
    ```bash
    python -m venv .venv
    source .venv/bin/activate  # Linux/Mac
    .venv\Scripts\activate     # Windows

3. Instalar el proyecto en modo editable:
    ```bash
    pip install -e .


## Para ejecutar
```bash
python -m proyecto_simon <command>

<command> : ["reserve","consult"]
"reserve" : Reservar cancha
"consult" : Consultar disponibilidad (Retorna JSON de disponibilidad)
