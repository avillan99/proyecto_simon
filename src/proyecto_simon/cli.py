import asyncio
import sys

from .flows import reserve, consult

COMMANDS = {
    "reserve": reserve,
    "consult": consult,
    # "status": status,
}

#Estadio
## Cancha 10: 293
## Cancha 8: 309
## Cancha 9: 311

# DIVISION_PK = 293

async def main():
    if len(sys.argv) < 2:
        raise SystemExit("Usage: python -m myproject <command>")
    
    command = sys.argv[1]
    args = sys.argv[2:]

    await COMMANDS[command](*args)

if __name__ == "__main__":
    asyncio.run(main())