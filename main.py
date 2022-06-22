import argparse
import os
import time
from concurrent.futures import ThreadPoolExecutor
from random import choice
from threading import local

import requests
from bs4 import BeautifulSoup
from requests.sessions import Session

thread_local = local()


def get_session() -> Session:
    if not hasattr(thread_local, 'session'):
        thread_local.session = requests.Session()
    return thread_local.session


def save_screenshot(screenshot_id: str, content: bytes) -> None:
    filename = f'screenshots/{screenshot_id}.png'
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    with open(filename, 'wb') as f:
        f.write(content)


def download_screenshot(url: str) -> None:
    screenshot_id = url[-6:]
    headers = {'user-agent': 'Mozilla/5.0'}
    session = get_session()
    with session.get(url, headers=headers) as r:
        soup = BeautifulSoup(r.text, features='html.parser')
        image = soup.find('img', {'class': 'no-click screenshot-image'}).get('src')
        print(image)
        with session.get(image, headers=headers) as r:
            save_screenshot(screenshot_id, r.content)


def generation_urls(amount: int) -> list:
    base_url = 'https://prnt.sc/'
    letters = 'qwertyuiopasdfghjklzxcvbnm'
    digits = '1234567890'
    urls = [base_url + ''.join(choice(letters + digits)
                               for char in range(6)) for i in range(amount)]
    return urls


def download(urls: list) -> None:
    with ThreadPoolExecutor() as executor:
        executor.map(download_screenshot, urls)


def get_arg() -> int:
    parser = argparse.ArgumentParser(description='prnt-screen-grab')
    required = parser.add_argument_group('required argument')
    required.add_argument('-a', '--amount', type=int, required=True,
                          help='number of screenshots to download')
    arg = parser.parse_args()

    if arg.amount < 1:
        parser.error('Minimum amount is 1')

    number_screenshots = arg.amount
    return number_screenshots


def main() -> None:
    amount_urls = get_arg()
    screenshots_urls = generation_urls(amount_urls)

    start = time.time()
    download(screenshots_urls)
    end = time.time()
    print(f'Downloaded {amount_urls} screenshots in {end - start} seconds.')


if __name__ == '__main__':
    main()
