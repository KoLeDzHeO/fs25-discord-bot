import os
import asyncio
import discord
from ftplib import FTP
import xml.etree.ElementTree as ET
from io import BytesIO
import json

TOKEN = os.getenv("DISCORD_TOKEN")
CHANNEL_ID = int(os.getenv("DISCORD_CHANNEL_ID"))
FTP_HOST = os.getenv("FTP_HOST")
FTP_PORT = int(os.getenv("FTP_PORT", "21"))
FTP_USER = os.getenv("FTP_USER")
FTP_PASS = os.getenv("FTP_PASS")
FTP_PATH = os.getenv("FTP_PATH")
FARM_ID = "1"

client = discord.Client(intents=discord.Intents.default())
last_messages = []

with open("fs25_vehicles.json", "r", encoding="utf-8") as f:
    vehicles = json.load(f)
name_map = {v["xml_key"].lower(): v["name_ru"] for v in vehicles if v.get("name_ru")}

def get_readable_name(raw_name):
    return name_map.get(raw_name.lower(), raw_name)

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
    vehicles = []
    try:
        root = ET.fromstring(xml_data)
        for vehicle in root.findall("vehicle"):
            if vehicle.attrib.get("farmId") != FARM_ID:
                continue
            filename_raw = vehicle.get("filename")
            if not filename_raw:
                continue
            filename = filename_raw.split("/")[-1].replace(".xml", "")
            name = get_readable_name(filename)
            dirt, damage, fuel = extract_vehicle_info(vehicle)
            line = f"{name} | Грязь: {int(dirt*100)}% | Повреждение: {int(damage*100)}% | Топливо: {int(fuel)}L"
            vehicles.append(line)
    except Exception as e:
        vehicles.append(f"Error parsing XML: {e}")
    return vehicles

def split_messages(lines, max_length=2000):
    blocks = []
    current = ""
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
    print(f"Bot started as {client.user}")
    await start_reporting()

async def start_reporting():
    global last_messages
    channel = client.get_channel(CHANNEL_ID)
    while True:
        for msg in last_messages:
            try:
                await msg.delete()
            except:
                pass
        last_messages.clear()
        xml_data = fetch_vehicles_xml()
        if xml_data:
            lines = parse_vehicles(xml_data)
        else:
            lines = ["Could not fetch data from FTP"]
        blocks = split_messages(lines)
        for block in blocks:
            try:
                sent = await channel.send(block)
                last_messages.append(sent)
            except Exception as e:
                print(f"Send error: {e}")
        await asyncio.sleep(30)

client.run(TOKEN)
