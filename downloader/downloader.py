import logging
import os
from typing import List, Union

import requests
from bs4 import BeautifulSoup
from requests.models import Response

logging.basicConfig(level=logging.INFO, format="%(message)s")


class GameNotFound(Exception):
    pass


class Item:
    def __init__(self, title: str, url: str):
        self._title = title
        self._url = url

    @property
    def url(self) -> str:
        return self._url

    def __eq__(self, other: Union[object, 'Item']) -> bool:
        if not isinstance(other, Item):
            return NotImplemented
        return self.url == other.url


class Downloader:
    def __init__(self, appid: int):
        self._appid = appid
        self._game_title = None

    def __repr__(self) -> str:
        return "{appid}:{game_title}".format(
            appid=self._appid,
            game_title=self._game_title or '未取得',
        )

    @property
    def appid(self) -> int:
        return self._appid

    @property
    def game_title(self) -> Union[str, None]:
        return self._game_title

    @property
    def trading_cards(self) -> List[Item]:
        return self._trading_cards

    @property
    def wallpapers(self) -> List[Item]:
        return self._wallpapers

    def fetch_page_data(self) -> None:
        response: Response = requests.get(
            "https://www.steamcardexchange.net/index.php?"
            + "gamepage-appid-{appid}".format(
                appid=self._appid)
        )
        response.raise_for_status()

        self._soup = BeautifulSoup(response.text, features="html.parser")

        try:
            self._game_title = self._soup.select_one(
                'div.game-title > h1').text
        except AttributeError as e:
            raise GameNotFound(f"{self._appid} has not found!") from e

        self._parse_trading_cards()
        self._parse_wallpapers()

    def _parse_trading_cards(self):
        card_element = self._soup.select(
            "div.showcase-element-container.card a.element-link-right")

        self._trading_cards: List[Item] = []

        for element in card_element:
            item: Item = Item(element.parent.img["alt"], element["href"])

            if item not in self._trading_cards:
                self._trading_cards.append(item)

    def _parse_wallpapers(self):
        wallpaper_element = self._soup.select(
            'div.showcase-element-container.background a.element-link-right')

        self._wallpapers: List[Item] = [
            Item(element.parent.img["alt"], element["href"])
            for element in wallpaper_element
        ]


def main(appid: int) -> None:
    url = f"https://www.steamcardexchange.net/index.php?gamepage-appid-{appid}"

    response: Response = requests.get(url)
    response.raise_for_status()

    soup: BeautifulSoup = BeautifulSoup(response.text, features="html.parser")
    game_title: str = soup.find("div", "game-title").text

    logging.info("Downloading %s - %s...", appid, game_title)

    os.makedirs(f"{game_title}/backgrounds", exist_ok=True)

    downloaded: List[str] = []
    elements = soup.select("a.element-link-right")

    for element in elements:
        title: str = element.parent.img["alt"]
        url: str = element["href"]

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
