import os
import asyncio
import discord
from ftplib import FTP
import xml.etree.ElementTree as ET
from io import BytesIO
from collections import defaultdict
from vehicle_filter import get_info_by_key

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
    "eggBoxPallet", "cementBagsPallet", "bigBag_seeds", "bigBagHelm_fertilizer",
    "bigBag_fertilizer", "goatMilkCanPallet", "roofPlatesPallet",
    "cementBricksPallet", "cementBoxPallet"
}

def fetch_vehicles_xml():
    try:
        ftp = FTP()
        ftp.connect(FTP_HOST, FTP_PORT)
        ftp.login(FTP_USER, FTP_PASS)
        buffer = BytesIO()
        ftp.retrbinary(f"RETR {FTP_PATH}", buffer.write)
        buffer.seek(0)
        ftp.quit()
        return buffer.getvalue()
    except Exception as e:
        print(f"FTP Error: {e}")
        return None

def extract_vehicle_info(vehicle):
    dirt = damage = fuel = 0
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

def parse_vehicles(xml_data):
    categories = defaultdict(list)
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
            if damage <= 0.05 and dirt <= 0.05 and (not max_fuel or fuel >= 0.8 * max_fuel):
                continue

            category = info.get("class") or "Разное"
            name = info.get("name_ru") or filename
            categories[category].append(name)
    except Exception as e:
        return [f"Ошибка разбора XML: {e}"]
    return format_output(categories)

def format_output(groups):
    result = []
    for cat, items in sorted(groups.items()):
        result.append(f"{cat}:")
        result.append("```")
        result.extend(items)
        result.append("```")
    return result

def split_messages(lines, max_length=2000):
    blocks, current = [], ""
    for line in lines:
        if len(current) + len(line) + 1 > max_length:
            blocks.append(current)
            current = ""
        current += line + "\n"
    if current:
        blocks.append(current)
    return blocks

@client.event
async def on_ready():
    print(f"Bot started как {client.user}")
    await start_reporting()

async def start_reporting():
    channel = client.get_channel(CHANNEL_ID)
    async for msg in channel.history(limit=None):
        if msg.author == client.user:
            try:
                await msg.delete()
            except:
                pass
    while True:
        xml_data = fetch_vehicles_xml()
        lines = parse_vehicles(xml_data) if xml_data else ["Ошибка получения данных с FTP"]
        for block in split_messages(lines):
            try:
                await channel.send(block)
            except Exception as e:
                print(f"Ошибка отправки: {e}")
        await asyncio.sleep(30)

client.run(TOKEN)
