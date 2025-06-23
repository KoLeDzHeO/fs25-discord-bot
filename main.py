import os
import asyncio
import discord
from ftplib import FTP
import xml.etree.ElementTree as ET
from io import BytesIO
import json
from collections import defaultdict

TOKEN = os.getenv("DISCORD_TOKEN")
CHANNEL_ID = int(os.getenv("DISCORD_CHANNEL_ID"))
FTP_HOST = os.getenv("FTP_HOST")
FTP_PORT = int(os.getenv("FTP_PORT", "21"))
FTP_USER = os.getenv("FTP_USER")
FTP_PASS = os.getenv("FTP_PASS")
FTP_PATH = os.getenv("FTP_PATH")
FARM_ID = "1"

with open("tech_filter_cleaned.json", "r", encoding="utf-8") as f:
    TECH_CATEGORIES = json.load(f)

CATEGORY_NAMES = {
    "tractorsM": "🚜 Тракторы",
    "cutters": "✂️ Жатки",
    "trailers": "🚛 Прицепы",
    "balers": "🧶 Пресс-подборщики",
    "sprayers": "💧 Опрыскиватели",
    "seeders": "🌱 Сеялки",
    "weights": "⚖️ Грузы",
    "unknown": "🧲 Прочее",
}

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

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
    categorized = defaultdict(list)
    try:
        root = ET.fromstring(xml_data)
        for vehicle in root.findall("vehicle"):
            if vehicle.attrib.get("farmId") != FARM_ID:
                continue

            name = vehicle.get("filename", "Неизвестно").split("/")[-1].replace(".xml", "")
            category = TECH_CATEGORIES.get(name, "unknown")
            readable_name = name.replace("_", " ").capitalize()

            fuel_level = 0.0
            fuel_capacity = 1.0
            fuel_str = "-"
            fillUnit = vehicle.find("fillUnit")
            if fillUnit is not None:
                for unit in fillUnit.findall("unit"):
                    if unit.attrib.get("fillType") == "DIESEL":
                        try:
                            fuel_level = float(unit.attrib.get("fillLevel", 0))
                            fuel_capacity = float(unit.attrib.get("capacity", 1))
                            fuel_str = f"{fuel_level:.0f}/{fuel_capacity:.0f}л"
                        except:
                            pass

            damage = "-"
            wearable = vehicle.find("wearable")
            if wearable is not None:
                try:
                    dmg = float(wearable.attrib.get("damage", 0))
                    damage = f"{dmg * 100:.1f}%"
                except:
                    pass

            dirt = "-"
            washable = vehicle.find("washable")
            if washable is not None:
                dirtNode = washable.find("dirtNode")
                if dirtNode is not None:
                    try:
                        dirt = f"{float(dirtNode.attrib.get('amount', 0)) * 100:.1f}%"
                    except:
                        pass

            line = f"{readable_name} | Топливо: {fuel_str} | Износ: {damage} | Грязь: {dirt}"
            categorized[category].append(line)

    except Exception as e:
        return f"❌ Ошибка при разборе XML: {str(e)}"

    final_lines = []
    for cat, lines in categorized.items():
        title = CATEGORY_NAMES.get(cat, cat.capitalize())
        section = f"{title}:
" + "
".join(lines)
        final_lines.append(section)

    return "

".join(final_lines)

@client.event
async def on_ready():
    print(f"✅ Бот запущен как {client.user}")
    channel = client.get_channel(CHANNEL_ID)
    while True:
        try:
            async for msg in channel.history(limit=50):
                if msg.author == client.user:
                    await msg.delete()
        except Exception as e:
            print(f"⚠️ Ошибка очистки: {e}")

        xml_data = fetch_vehicles_xml()
        result = ""
        if xml_data:
            result = parse_vehicles(xml_data)
        else:
            result = "❌ Не удалось подключиться к FTP"

        try:
            await channel.send(result[:2000])
        except Exception as send_err:
            print(f"Ошибка при отправке: {send_err}")

        await asyncio.sleep(60)

client.run(TOKEN)
