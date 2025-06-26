import os
import asyncio
import discord
import ftplib
import xml.etree.ElementTree as ET
from io import BytesIO
from typing import Iterable
from vehicle_filter import get_info_by_key
from classify_vehicles import classify_vehicles
from models import Vehicle

last_messages: list[discord.Message] = []

# === CONFIG ===
TOKEN = os.getenv("DISCORD_TOKEN")
CHANNEL_ID = int(os.getenv("DISCORD_CHANNEL_ID"))
FTP_HOST = os.getenv("FTP_HOST")
FTP_PORT = int(os.getenv("FTP_PORT", "21"))
FTP_USER = os.getenv("FTP_USER")
FTP_PASS = os.getenv("FTP_PASS")
FTP_PATH = os.getenv("FTP_PATH")
FARM_ID = "1"

client = discord.Client(intents=discord.Intents.default())

SKIP_OBJECTS = {
    "eggBoxPallet",
    "cementBagsPallet",
    "bigBag_seeds",
    "bigBagHelm_fertilizer",
    "bigBag_fertilizer",
    "goatMilkCanPallet",
    "roofPlatesPallet",
    "cementBricksPallet",
    "cementBoxPallet",
}


async def fetch_vehicles_xml() -> bytes | None:
    """Download the vehicles XML via FTP."""

    def _download() -> bytes:
        with ftplib.FTP() as ftp:
            ftp.connect(FTP_HOST, FTP_PORT)
            ftp.login(FTP_USER, FTP_PASS)
            buffer = BytesIO()
            ftp.retrbinary(f"RETR {FTP_PATH}", buffer.write)
            buffer.seek(0)
            return buffer.getvalue()

    try:
        return await asyncio.to_thread(_download)
    except Exception as e:
        print(f"FTP Error: {e}")
        return None


def extract_vehicle_info(vehicle) -> tuple[float, float, float]:
    """Return dirt, damage and fuel levels for the given XML element."""
    dirt = damage = fuel = 0.0
    dirt_elem = vehicle.find(".//washable/dirtNode")
    if dirt_elem is not None:
        dirt = float(dirt_elem.attrib.get("amount", 0))
    damage_elem = vehicle.find("wearable")
    if damage_elem is not None:
        damage = float(damage_elem.attrib.get("damage", 0))
    for unit in vehicle.findall(".//fillUnit/unit"):
        if unit.attrib.get("fillType", "").lower() == "diesel":
            fuel = float(unit.attrib.get("fillLevel", 0))
            break
    return dirt, damage, fuel


def collect_vehicles(xml_data: bytes) -> list[Vehicle]:
    """Parse XML data into a list of :class:`Vehicle` objects."""
    result: list[Vehicle] = []
    try:
        root = ET.fromstring(xml_data)
        for vehicle in root.findall("vehicle"):
            if vehicle.attrib.get("farmId") != FARM_ID:
                continue
            filename_raw = vehicle.get("filename")
            if not filename_raw:
                continue
            filename = filename_raw.split("/")[-1].replace(".xml", "")
            if filename in SKIP_OBJECTS:
                continue

            dirt, damage, fuel = extract_vehicle_info(vehicle)
            info = get_info_by_key(filename)
            max_fuel = info.get("fuel_capacity") or 0
            uses_fuel = info.get("uses_fuel", bool(max_fuel))

            if (
                damage <= 0.05
                and dirt <= 0.05
                and (not max_fuel or fuel >= 0.8 * max_fuel)
            ):
                continue

            result.append(
                Vehicle(
                    name=info.get("name") or filename,
                    dirt=dirt * 100,
                    damage=damage * 100,
                    fuel=fuel,
                    fuel_capacity=max_fuel,
                    uses_fuel=uses_fuel,
                )
            )
    except Exception as e:
        print(f"Ошибка разбора XML: {e}")
    return result


def split_messages(lines: Iterable[str], max_length: int = 2000) -> list[str]:
    """Split text into Discord-friendly messages."""
    blocks: list[str] = []
    current = ""

    for section in lines:
        for line in section.splitlines(keepends=True):
            if len(current) + len(line) > max_length:
                blocks.append(current.rstrip())
                current = ""
            current += line
        if len(current) > max_length:
            blocks.append(current.rstrip())
            current = ""

    if current.strip():
        blocks.append(current.rstrip())

    return blocks


@client.event
async def on_ready():
    print(f"Бот запущен как {client.user}")
    await start_reporting()


async def start_reporting():
    global last_messages
    channel = client.get_channel(CHANNEL_ID)

    if not channel:
        print(
            f"❌ Канал с ID {CHANNEL_ID} не найден! Проверь переменную DISCORD_CHANNEL_ID."
        )
        return
    else:
        print(f"✅ Канал найден: {channel.name} ({channel.id})")

    # Удаляем все предыдущие сообщения от бота
    async for msg in channel.history(limit=None):
        if msg.author == client.user:
            try:
                await msg.delete()
            except Exception as e:
                print(f"⚠️ Не удалось удалить сообщение: {e}")

    while True:
        for msg in last_messages:
            try:
                await msg.delete()
            except:
                pass
        last_messages.clear()

        xml_data = await fetch_vehicles_xml()
        if not xml_data:
            print("❌ Не удалось получить XML с FTP")
            msg = await channel.send("❌ Не удалось подключиться к FTP")
            last_messages.append(msg)
            await asyncio.sleep(30)
            continue
        else:
            print("✅ XML получен")

        vehicles = collect_vehicles(xml_data)
        if not vehicles:
            print("ℹ️ Нет техники для обслуживания")
            msg = await channel.send("ℹ️ Нет техники для обслуживания")
            last_messages.append(msg)
            await asyncio.sleep(30)
            continue

        markdown = classify_vehicles(vehicles)

        for block in split_messages([markdown]):
            try:
                sent = await channel.send(block)
                last_messages.append(sent)
            except Exception as e:
                print(f"Ошибка отправки: {e}")

        await asyncio.sleep(600)


client.run(TOKEN)
