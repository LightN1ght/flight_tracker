import os
from pathlib import Path

from dotenv import load_dotenv

from src.api import APIError, NOMINATIM_URL, OpenSkyAircraftAPI
from src.cli import user_interaction
from src.json_saver import JSONSaver


def main() -> None:
    """Запускает программу поиска самолётов."""
    load_dotenv(Path(__file__).with_name(".env"))

    try:
        api = OpenSkyAircraftAPI(
            nominatim_url=os.getenv("NOMINATIM_URL") or NOMINATIM_URL,
            client_id=os.getenv("OPENSKY_CLIENT_ID"),
            client_secret=os.getenv("OPENSKY_CLIENT_SECRET"),
        )
    except APIError as error:
        print(f"Программа: {error}")
        return

    user_interaction(api, JSONSaver())


if __name__ == "__main__":
    main()
