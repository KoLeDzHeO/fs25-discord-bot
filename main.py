import os
import asyncio
import discord
from ftplib import FTP
import xml.etree.ElementTree as ET
from io import BytesIO
import json

# === CONFIGURATION ===
TOKEN = os.getenv("DISCORD_TOKEN")
CHANNEL_ID = int(os.getenv("DISCORD_CHANNEL_ID"))
FTP_HOST = os.getenv("FTP_HOST")
FTP_PORT = int(os.getenv("FTP_PORT", "21"))
FTP_USER = os.getenv("FTP_USER")
FTP_PASS = os.getenv("FTP_PASS")
FTP_PATH = os.getenv("FTP_PATH")
FARM_ID = "1"

# === DISCORD SETUP ===
intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)
last_messages = []

# === LOAD NAME MAP ===
with open("vehicle_names_cleaned_final.json", "r", encoding="utf-8") as f:
    name_map = json.load(f)

def get_readable_name(raw_name: str) -> str | None:
    return name_map.get(raw_name.lower())

def mark(value: float, danger: float, warning: float, unit: str = "%") -> str:
    val = int(value) if unit != " л" else int(round(value))
    if value >= danger:
        return f"🟥 {val}{unit}"
    elif value >= warning:
        return f"🟨 {val}{unit}"
    return f"✅ {val}{unit}" if unit != " л" else f"🔋 {val} л"

def fetch_vehicles_xml() -> bytes | None:
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

def extract_status(vehicle: ET.Element) -> tuple[float, float, float]:
    dirt = 0
    damage = 0
    fuel = 0
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

def format_vehicle_line(readable: str, dirt: float, damage: float, fuel: float) -> tuple[str, str]:
    if "—" in readable:
        category, name = readable.split("—", 1)
        category = category.strip()
    else:
        category, name = "Другое", readable
    dirt_txt = f"{int(dirt * 100)}%"
    damage_txt = f"{int(damage * 100)}%"
    fuel_txt = f"{int(fuel)} л"
    line = f"{name.strip():<20} | Грязь: {dirt_txt} | Поврежд.: {damage_txt} | Топливо: {fuel_txt}"
    return category, line

def parse_vehicles(xml_data: bytes) -> dict[str, list[str]]:
    groups = {}
    try:
        root = ET.fromstring(xml_data)
        for vehicle in root.findall("vehicle"):
            if vehicle.attrib.get("farmId") != FARM_ID:
                continue
            filename = vehicle.get("filename", "").split("/")[-1].replace(".xml", "")
            readable = get_readable_name(filename)
            if not readable:
                continue
            dirt, damage, fuel = extract_status(vehicle)
            group_key, formatted_line = format_vehicle_line(readable, dirt, damage, fuel)
            groups.setdefault(group_key, []).append((formatted_line, damage))
    except Exception as e:
        return {"Ошибки": [f"❌ Ошибка XML: {str(e)}"]}

    final = {}
    for group, entries in sorted(groups.items()):
        lines = [line for line, _ in sorted(entries, key=lambda x: -x[1])]
        final[group.strip("* ").strip()] = lines
    return final

def split_message_blocks(grouped_data: dict[str, list[str]], max_length: int = 2000) -> list[str]:
    blocks = []
    current = ""

    for category, lines in grouped_data.items():
        header = f"\n**{category}:**\n```
"
        footer = "```"

        block = header
        for line in lines:
            if len(block) + len(line) + len(footer) + 1 > max_length:
                block += footer
                blocks.append(block.strip())
                block = header + line + "\n"
            else:
                block += line + "\n"
        block += footer
        blocks.append(block.strip())

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
        parsed = parse_vehicles(xml_data) if xml_data else {"Ошибки": ["❌ Не удалось получить данные с FTP"]}
        blocks = split_message_blocks(parsed)
        for chunk in blocks:
            try:
                sent = await channel.send(chunk)
                last_messages.append(sent)
            except Exception as e:
                print(f"Ошибка отправки: {e}")
        await asyncio.sleep(30)

client.run(TOKEN)
