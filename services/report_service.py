import requests
from config import Config


def dashboard():

    response = requests.get(
        f"{Config.REPORTS_API}/reports/dashboard"
    )

    if response.status_code == 200:
        return response.json()

    return {}


def gender_distribution():

    response = requests.get(
        f"{Config.REPORTS_API}/reports/gender"
    )

    if response.status_code == 200:
        return response.json()

    return []


def age_distribution():

    response = requests.get(
        f"{Config.REPORTS_API}/reports/age-groups"
    )

    if response.status_code == 200:
        return response.json()

    return []


def purok_distribution():

    response = requests.get(
        f"{Config.REPORTS_API}/reports/purok"
    )

    if response.status_code == 200:
        return response.json()

    return []