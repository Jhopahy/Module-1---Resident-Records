import requests
from config import Config


def get_resident(resident_id):

    response = requests.get(
        f"{Config.RESIDENTS_API}/residents/{resident_id}/basic"
    )

    if response.status_code == 200:
        return response.json()

    return None


def resident_exists(resident_id):

    response = requests.get(
        f"{Config.RESIDENTS_API}/residents/{resident_id}/exists"
    )

    if response.status_code == 200:
        return response.json()["exists"]

    return False


def get_all_residents():

    response = requests.get(
        f"{Config.RESIDENTS_API}/residents"
    )

    if response.status_code == 200:
        return response.json()

    return []


def get_population_count():

    response = requests.get(
        f"{Config.RESIDENTS_API}/residents/count"
    )

    if response.status_code == 200:
        return response.json()["total"]

    return 0