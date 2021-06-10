import requests
import time
from bs4 import BeautifulSoup

DAFT_URLS = [
    r"https://www.daft.ie/property-for-rent/ireland/houses?sort=publishDateDesc",  # Hoses to rent
    r'https://www.daft.ie/property-for-rent/ireland/apartments?sort=publishDateDesc',  # Apartments to rent
    r'https://www.daft.ie/property-for-rent/ireland/studio-apartments?sort=publishDateDesc',
    # Studio apartments to rent
    r'https://www.daft.ie/sharing/ireland/houses?sort=publishDateDesc',  # Hoses to share
    r'https://www.daft.ie/sharing/ireland/apartments?sort=publishDateDesc',  # Apartment to share
    r'https://www.daft.ie/sharing/ireland?sort=publishDateDesc&roomType=shared',  # Room share
]

RENT_IE_URLS = [
    r'https://www.rent.ie/houses-to-let/renting_dublin/sort-by_date-entered_down/'
    r'https://www.rent.ie/houses-to-let/renting_cork/sort-by_date-entered_down/'
    r'https://www.rent.ie/houses-to-let/renting_galway/sort-by_date-entered_down/'
    r'https://www.rent.ie/houses-to-let/renting_limerick/sort-by_date-entered_down/'
]

LETIE = ['https://www.let.ie/property-to-rent/The-Avenue-Garrane-Dara/3874792']

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36",
    "accept": "*/*"}


def get_data(url, params=None):
    while True:
        try:
            data = requests.get(url, headers=HEADERS, params=params, timeout=1)
            break
        except requests.exceptions.ConnectionError:
            time.sleep(120)
    return data.text


def get_rental_daft(data):
    soup = BeautifulSoup(data, "html.parser")
    items = soup.find_all(class_='SearchPage__Result-gg133s-2')
    prop_in_db = db_halper.slect_prop_id()
    for i in items:
        try:
            link = 'https://www.daft.ie' + i.a.get('href')
            id_p = link.split('/')[-1]
            if int(id_p) in prop_in_db:
                continue
            district = i.find(class_='TitleBlock__Address-sc-1avkvav-7').text.split(',')[-1].strip()
            city = district

            if 'Dublin' in district:
                city = 'Dublin'

            description = i.find(class_='TitleBlock__CardInfo-sc-1avkvav-9').get_text(
                separator=', ')
            type_of_rent = 'None'
            if '/for-rent/apartment' in link and 'studio' not in link:
                type_of_rent = 1
            elif '/for-rent/house' in link:
                type_of_rent = 0
            elif '/for-rent/studio' in link:
                type_of_rent = 2
            elif '/share/' in link and description.split()[-1].lower() == 'house' and description.split()[
                -3].lower().strip() != 'shared':
                type_of_rent = 3
            elif '/share/' in link and description.split()[-1].lower() == 'apartment' and description.split()[
                -3].lower().strip() != 'shared':
                type_of_rent = 4
            elif '/share/' in link and description.split()[-1].lower() == 'flat' and description.split()[
                -3].lower().strip() != 'shared':
                type_of_rent = 5
            elif '/share/' in link and description.split()[-2].lower().strip() == 'room,':
                type_of_rent = 6
            detail_price = i.find(class_='TitleBlock__StyledSpan-sc-1avkvav-4').text.replace('From', '').strip()
            price = detail_price.split(' ')[0].replace('€', '').replace('£', '').replace(',', '')
            address = i.find(class_='TitleBlock__Address-sc-1avkvav-7').text.strip()
            sent_status = 0
            properties = (
                id_p, time.time(), link, city, district, type_of_rent, float(price), detail_price, address, description,
                sent_status)
            # save to DB
        except Exception as es:
            db_halper.save_errors(f'pars daft: {es}')


def get_rental_rentalie(html):
    soup = BeautifulSoup(html, "html.parser")
    items = soup.find_all(class_="search_result")
    prop_in_db = db_halper.slect_prop_id()
    for i in items:
        try:
            link = i.find(class_='sresult_image_container').a.get('href')
            id_p = link.split('/')[-2]
            if int(id_p) in prop_in_db:
                continue
            city = i.h2.text.split()[-2]
            district = i.h2.text.split(',')[-1].strip()
            if city == 'Co.':
                city = 'Dublin'
                district = 'Co. Dublin'
            type_of_rent = None
            if 'houses-to-let' in link:
                type_of_rent = 0
            detail_price = i.find(class_='sresult_description').h4.text.strip()
            price = detail_price.split(' ')[0].replace('€', '').replace('£', '').replace(',', '')
            description = i.find(class_='sresult_description').h3.text.strip()
            sent_status = 0
            address = i.h2.a.text.strip()
            properties = (
                id_p, time.time(), link, city, district, type_of_rent, float(price), detail_price, address, description,
                sent_status)
            # save to DB
        except Exception as es:
            db_halper.save_errors(f'pars rental: {es}')


if __name__ == '__main__':
    while True:
        for url in DAFT_URLS:
            get_rental_daft(get_data(url))

        for url1 in RENT_IE_URLS:
            get_rental_rentalie(get_data(url1))
        time.sleep(60)
