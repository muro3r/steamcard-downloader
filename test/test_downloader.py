import downloader
import pytest
import responses


def test_downloader():
    app = downloader.Downloader(appid=100)

    assert app.appid == 100
    assert app.game_title is None


@responses.activate
def test_fetch_data():
    with open("test/gamepage-appid-620.html") as f:
        body = f.read()

    app = downloader.Downloader(appid=620)
    responses.add(
        responses.GET,
        'https://www.steamcardexchange.net/index.php?gamepage-appid-620',
        body=body,
    )

    cards_url = 'https://steamcdn-a.akamaihd.net/steamcommunity/public/images/items/620/'
    trading_cards = [
        downloader.Item('Chell',
                        cards_url + '288089285a954b6d1cf5c40c4fe221a071f50a71.jpg'),
        downloader.Item('Destruction',
                        cards_url + '6fa10bdb8b9869382440f5de23b9f27a795fbe69.jpg'),
        downloader.Item('Finale',
                        cards_url + 'bee530fb688af1acfc73ea186f77dc16a60b6bd6.jpg'),
        downloader.Item('GlaDOS',
                        cards_url + 'aed066348b7cdb7d93386a72f0800496a99d73e4.jpg'),
        downloader.Item('Intro',
                        cards_url + '28b25bb2317111ca6c45108a19bb121696ca7d0a.jpg'),
        downloader.Item('The lab',
                        cards_url + '0bc3a1d870dc550ae02ed1273be5fc6017f83dc1.jpg'),
        downloader.Item('Mannequin',
                        cards_url + 'adfda56ffb40771ea607a77f9ea31cf3208b2a37.png'),
        downloader.Item('Underground',
                        cards_url + 'fbdf17161fae8b6a93099434285e4b3d9db97dcb.jpg'),
    ]

    background_url = 'https://steamcommunity.com/economy/profilebackground/items/620/'
    wallpapers = [
        downloader.Item('Bots',
                        background_url + 'a479809817527090dbd3dac5664b71dddfa47dee.jpg'),
        downloader.Item('Portal 2 Logo',
                        background_url + 'aae901f5cca93fb9f50fd4746535d24cd572b5b4.jpg'),
        downloader.Item('Turrets',
                        background_url + 'aef3f9a49b097d61b0b76b1bbe2bfc145fd169a8.jpg'),
        downloader.Item('Intro',
                        background_url + '904c34bd20f5a5f5eadb074cce42d2606b266acc.jpg'),
        downloader.Item('Bot Blueprint',
                        background_url + '587fe7e1cd995174f039a4d28f25f2a5caa96329.jpg'),
    ]

    app.fetch_page_data()

    assert app.game_title == 'Portal 2'
    assert repr(app) == '620:Portal 2'
    assert app.trading_cards == trading_cards
    assert app.wallpapers == wallpapers


@responses.activate
def test_not_found_error():
    responses.add(
        'GET',
        'https://www.steamcardexchange.net/index.php?gamepage-appid-404',
        body='')

    app = downloader.Downloader(appid=404)

    with pytest.raises(downloader.GameNotFound) as e:
        app.fetch_page_data()

    assert '404 has not found!' in str(e)
