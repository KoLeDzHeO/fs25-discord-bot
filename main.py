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
    return name_map.get(name.lower(), None)

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

def parse_vehicles(xml_data):
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

            icon = readable[0]
            if "—" in readable:
                category_text = readable.split("—")[0].strip().replace(icon, "").strip()
                name = readable.split("—")[1].strip()
            else:
                category_text = "Другое"
                name = readable

            dirt_elem = vehicle.find(".//washable/dirtNode")
            dirt = float(dirt_elem.attrib.get("amount", 0)) if dirt_elem is not None else 0

            damage_elem = vehicle.find("wearable")
            damage = float(damage_elem.attrib.get("damage", 0)) if damage_elem is not None else 0

            fuel = 0
            for unit in vehicle.findall(".//fillUnit/unit"):
                if unit.attrib.get("fillType", "").lower() == "diesel":
                    fuel = float(unit.attrib.get("fillLevel", 0))
                    break

            def mark(value, danger, warning, unit="%"):
                if value >= danger:
                    return f"🟥 {int(value)}{unit}"
                elif value >= warning:
                    return f"🟨 {int(value)}{unit}"
                return f"✅ {int(value)}{unit}"

            dirt_txt = mark(dirt * 100, 70, 40)
            damage_txt = mark(damage * 100, 10, 5)
            fuel_txt = mark(fuel, 1, 0, " л") if fuel == 0 else f"🔋 {int(fuel)} л"

            line = f"{icon} {name:<20} | Грязь: {dirt_txt} | Поврежд.: {damage_txt} | Топливо: {fuel_txt}"

            group_key = f"{icon} {category_text}"
            if group_key not in groups:
                groups[group_key] = []
            groups[group_key].append(line)

    except Exception as e:
        return [f"❌ Ошибка XML: {str(e)}"]

    for cat in groups:
        groups[cat].sort(key=lambda l: -int(l.split("Поврежд.: ")[1].split('%')[0].replace("🟥", "").replace("🟨", "").replace("✅", "").strip()))

    result = []
    for group, entries in groups.items():
        result.append(f"\n**{group}:**")
        result.extend(entries)
    return result

def icon_to_title(icon):
    return {
        "🚜": "Техника",
        "🌾": "Сельхозтехника",
        "⚖️": "Противовесы",
        "🚛": "Прицепы",
        "📦": "Навесное оборудование",
        "🛢️": "Бочки",
        "🍃": "Сгребатели",
        "🔄": "Обмотчики",
        "🔧": "Инструменты",
        "🔵": "Катки",
        "🪨": "Камнеуборщики",
        "💩": "Разбрасыватели",
        "🧪": "Опрыскиватели",
        "🌲": "Лесная техника",
        "🚗": "Машины"
    }.get(icon, "Другое")

def split_message_blocks(lines, max_length=2000):
    blocks = []
    current_block = ""
    for line in lines:
        if len(current_block) + len(line) + 1 > max_length:
            blocks.append(current_block.strip())
            current_block = ""
        current_block += line + "\n"
    if current_block:
        blocks.append(current_block.strip())
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
        if xml_data:
            lines = parse_vehicles(xml_data)
        else:
            lines = ["❌ Не удалось получить данные с FTP"]

        chunks = split_message_blocks(lines)
        for chunk in chunks:
            try:
                sent = await channel.send(chunk)
                last_messages.append(sent)
            except Exception as e:
                print(f"Ошибка отправки: {e}")

        await asyncio.sleep(30)

client.run(TOKEN)
