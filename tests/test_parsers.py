import pytest

from bot.parsers import (
    parse_server_stats,
    parse_farm_money,
    _count_vehicles,
    parse_farmland,
    parse_players_online,
    parse_last_month_profit,
)


def test_parse_server_stats_success():
    xml = (
        "<Server name='TestServer' mapName='TestMap'>"
        "<Slots capacity='16' numUsed='5'/><Stats saveDateFormatted='2024-01-01'/>"
        "</Server>"
    )
    result = parse_server_stats(xml)
    assert result == ("TestServer", "TestMap", 5, 16, "2024-01-01")


def test_parse_server_stats_error():
    # malformed XML should return tuple of None values
    result = parse_server_stats("<Server>")
    assert result == (None, None, None, None, None)


def test_parse_farm_money():
    xml = "<careerSavegame><statistics><money>1234</money></statistics></careerSavegame>"
    assert parse_farm_money(xml) == 1234


def test_parse_farm_money_invalid():
    xml = "<careerSavegame><statistics><money>bad</money></statistics></careerSavegame>"
    assert parse_farm_money(xml) is None


def test_count_vehicles():
    xml = (
        "<vehicles>"
        "<vehicle farmId='1' filename='data/tractor.xml'/>"
        "<vehicle farmId='1' filename='pallet.xml'/>"  # ignored keyword
        "<vehicle farmId='2' filename='data/car.xml'/>"
        "</vehicles>"
    )
    assert _count_vehicles(xml, "1") == 1


def test_count_vehicles_no_farmid():
    xml = "<vehicles><vehicle filename='data/tractor.xml'/></vehicles>"
    assert _count_vehicles(xml, "1") is None


def test_parse_farmland():
    xml = (
        "<map>"
        "<Farmland id='1' farmId='1'/>"
        "<Farmland id='2' farmId='2'/>"
        "<Farmland id='3'/>"
        "</map>"
    )
    assert parse_farmland(xml, "1") == (1, 3)


def test_parse_players_online():
    xml = (
        "<root><Slots>"
        "<Player isUsed='true'>John</Player>"
        "<Player isUsed='false'>Jane</Player>"
        "<Player isUsed='true'>-</Player>"
        "</Slots></root>"
    )
    assert parse_players_online(xml) == ["John"]


def test_parse_last_month_profit():
    xml = (
        "<root>"
        "<farm farmId='1'><finances><stats day='4'>"
        "<income>100.5</income><expense>-20</expense>"
        "</stats></finances></farm>"
        "</root>"
    )
    assert parse_last_month_profit(xml) == 80
