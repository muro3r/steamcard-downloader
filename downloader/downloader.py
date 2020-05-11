import logging
import os

import requests
from bs4 import BeautifulSoup


logging.basicConfig(level=logging.INFO, format="%(message)s")


def main(appid: int) -> None:
    url = f"https://www.steamcardexchange.net/index.php?gamepage-appid-{appid}"

    r = requests.get(url)
    r.raise_for_status()

    bs = BeautifulSoup(r.text, features="html.parser")
    game_title = bs.find("div", "game-title").text

    logging.info("Downloading %s - %s...", appid, game_title)

    os.makedirs(f"{game_title}/backgrounds", exist_ok=True)

    downloaded = []
    elements = bs.select("a.element-link-right")

    for element in elements:
        title = element.parent.img["alt"]
        url = element["href"]

        if url in downloaded:
            continue

        downloaded.append(url)

        data = requests.get(url)
        data.raise_for_status()

        filename = f"{game_title}/{title}.jpg"
        if "profilebackground" in url:
            filename = f"{game_title}/backgrounds/{title}.jpg"

        with open(filename, "wb") as f:
            f.write(data.content)

            logging.info("Downloaded! %s", filename)
