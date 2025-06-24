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

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)
last_messages = []

with open("vehicle_names_cleaned_final.json", "r", encoding="utf-8") as f:
    name_map = json.load(f)

def get_readable_name(name):
    return name_map.get(name.lower())

def classify_equipment(readable_name: str) -> str:
    categories = {
        "трактор": "powered",
        "машина": "powered",
        "комбайн": "powered_with_cargo",
        "прицеп": "cargo",
        "бочка": "cargo",
        "автопогрузчик": "powered",
        "форвардер": "powered_with_cargo",
        "жадка": "passive",
        "культиватор": "passive",
        "плуг": "passive",
        "сеялка": "cargo",
        "разбрасыватель": "cargo",
        "сгребатель": "passive",
        "камнеуборщик": "passive",
        "каток": "passive",
        "опрыскиватель": "cargo",
        "платформа": "passive"
    }
    lower = readable_name.lower()
    for key in categories:
        if key in lower:
            return categories[key]
    return "unknown"

def dotfill(name: str, width: int = 28) -> str:
    name = name[:width] if len(name) > width else name
    dots = '.' * (width - len(name))
    return name + dots

def format_line_by_class(name, dirt, damage, fuel, fill_type, fill_level, readable):
    type_class = classify_equipment(readable)
    parts = []

    if type_class in ("powered", "powered_with_cargo"):
        parts.append(f"{int(fuel)}л")
    if type_class in ("powered", "powered_with_cargo", "cargo", "passive"):
        parts.append(f"{int(damage * 100)}%")
        parts.append(f"{int(dirt * 100)}%")
    if type_class in ("powered_with_cargo", "cargo"):
        if fill_type and fill_type.lower() != "diesel" and fill_level > 0:
            parts.append(f"{fill_type} — {int(fill_level)}л")
        else:
            parts.append("пустой")

    return dotfill(name) + "  " + " | ".join(parts)

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

def extract_status(vehicle):
    dirt = damage = fuel = 0
    fill_type = ""
    fill_level = 0
    dirt_elem = vehicle.find(".//washable/dirtNode")
    if dirt_elem is not None:
        dirt = float(dirt_elem.attrib.get("amount", 0))
    damage_elem = vehicle.find("wearable")
    if damage_elem is not None:
        damage = float(damage_elem.attrib.get("damage", 0))
    for unit in vehicle.findall(".//fillUnit/unit"):
        unit_type = unit.attrib.get("fillType", "").lower()
        level = float(unit.attrib.get("fillLevel", 0))
        if unit_type == "diesel":
            fuel = level
        elif level > 0:
            fill_type = unit_type
            fill_level = level
    return dirt, damage, fuel, fill_type, fill_level

def parse_vehicles(xml_data):
    lines = []
    try:
        root = ET.fromstring(xml_data)
        for vehicle in root.findall("vehicle"):
            if vehicle.attrib.get("farmId") != FARM_ID:
                continue
            filename = vehicle.get("filename", "").split("/")[-1].replace(".xml", "")
            readable = get_readable_name(filename)
            if not readable:
                continue
            if "—" in readable:
                _, name = readable.split("—", 1)
            else:
                name = readable
            dirt, damage, fuel, fill_type, fill_level = extract_status(vehicle)
            line = format_line_by_class(name.strip(), dirt, damage, fuel, fill_type, fill_level, readable)
            lines.append(line)
    except Exception as e:
        return [f"❌ Ошибка XML: {str(e)}"]
    return lines

def split_message_blocks(lines, max_length=2000):
    blocks = []
    current = ""
    for line in lines:
        if len(current) + len(line) + 1 > max_length:
            blocks.append(f"```\n{current.strip()}\n```")
            current = ""
        current += line + "\n"
    if current:
        blocks.append(f"```\n{current.strip()}\n```")
    return blocks

@client.event
async def on_ready():
    print(f"✅ Бот запущен как {client.user}")
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
        lines = parse_vehicles(xml_data) if xml_data else ["❌ Не удалось получить данные с FTP"]
        for chunk in split_message_blocks(lines):
            try:
                sent = await channel.send(chunk)
                last_messages.append(sent)
            except Exception as e:
                print(f"Ошибка отправки: {e}")
        await asyncio.sleep(30)

client.run(TOKEN)
