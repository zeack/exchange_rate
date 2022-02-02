import requests
from bs4 import BeautifulSoup
from decimal import Decimal
from datetime import datetime, date
from requests.exceptions import RequestException

from django.conf import settings


def get_banxico_rate():
    """
    Returns the latest exchange rate of US dollars in Mexican peso
    from Banxico, date and the boolean if it was updated.
    """
    url = (
        'https://www.banxico.org.mx/SieAPIRest/service/v1/series/SF43718/datos/oportuno'
    )
    headers = {
        'Bmx-Token': settings.BANXICO_TOKEN,
        'Accept': 'application/xml',
    }
    try:
        req = requests.get(url, headers=headers)
    except RequestException:
        return None

    if req.ok and req.status_code == 200:
        soup = BeautifulSoup(req.text, 'lxml')
        rate = Decimal(soup.find('obs').find('dato').text)
        d = datetime.strptime(
            soup.find('obs').find('fecha').text,
            '%d/%m/%Y',
        ).date()
        return {
            'date': d,
            'rate': rate,
        }
    else:
        return None


def get_dof_rate():
    """
    Returns the latest exchange rate of US dollars in Mexican peso
    from DOF, date and the boolean if it was updated.
    """
    url = 'https://www.banxico.org.mx/tipcamb/tipCamMIAction.do'
    try:
        req = requests.get(url)
    except RequestException:
        return None

    if req.ok and req.status_code == 200:
        soup = BeautifulSoup(req.text, 'html.parser')
        for i in range(5, 28, 4):
            temp_date = soup.find_all('table')[8].find_all('td')[i].text
            temp_rate = soup.find_all('table')[8].find_all('td')[i+1].text
            if 'N/E' not in temp_rate:
                break

        d = datetime.strptime(
            temp_date.replace('\r\n', '').strip(),
            '%d/%m/%Y',
        ).date()
        temp_rate = temp_rate.replace('\r\n', '').strip()
        if temp_rate == 'N/E':
            return None
        else:
            rate = Decimal(temp_rate)
        return {
            'date': d,
            'rate': rate,
        }
    else:
        return None


def get_fixer_rate():
    """
    Returns the latest exchange rate of US dollars in Mexican peso
    from Fixer API, date and the boolean if it was updated.
    """
    url = f'http://data.fixer.io/api/latest?access_key={settings.FIXER_TOKEN}&symbols=USD,MXN'
    try:
        req = requests.get(url)
    except RequestException:
        return None

    if req.ok and req.status_code == 200:
        data = req.json()
        if data['base'] == 'EUR':
            rate = Decimal(data['rates']['MXN']) / Decimal(data['rates']['USD'])

        elif data['base'] == 'USD':
            rate = Decimal(data['rates']['MXN'])

        return {
            'date': date.fromisoformat(data['date']),
            'rate': rate.quantize(Decimal('.0001')),
        }
    else:
        return None
