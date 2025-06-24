import os
import asyncio
import discord
from ftplib import FTP
import xml.etree.ElementTree as ET
from io import BytesIO
import json

# === CONFIG ===
TOKEN = os.getenv("DISCORD_TOKEN")
CHANNEL_ID = int(os.getenv("DISCORD_CHANNEL_ID"))
FTP_HOST = os.getenv("FTP_HOST")
FTP_PORT = int(os.getenv("FTP_PORT", "21"))
FTP_USER = os.getenv("FTP_USER")
FTP_PASS = os.getenv("FTP_PASS")
FTP_PATH = os.getenv("FTP_PATH")
FARM_ID = "1"

# === DISCORD CLIENT ===
intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)
last_message = None

# === ЗАГРУЗКА СЛОВАРЯ ИМЁН ===
with open("vehicle_names_with_categories_updated.json", "r", encoding="utf-8") as f:
    name_map = json.load(f)

def get_readable_name(name):
    return name_map.get(name, f"🚜 Техника — {name}")

# === FTP ===
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

# === ПАРСИНГ XML ===
def parse_vehicles(xml_data):
    lines = []
    try:
        root = ET.fromstring(xml_data)
        for vehicle in root.findall("vehicle"):
            if vehicle.attrib.get("farmId") != FARM_ID:
                continue

            name = vehicle.get("filename", "Неизвестно").split("/")[-1].replace(".xml", "")
            readable_name = get_readable_name(name)

            line = f"{readable_name}"
            lines.append(line)

    except Exception as e:
        return [f"❌ Ошибка XML: {str(e)}"]

    return lines

# === ОБРАБОТКА СООБЩЕНИЙ ===
@client.event
async def on_ready():
    print(f"✅ Бот запущен как {client.user}")
    await start_reporting()

async def start_reporting():
    global last_message
    channel = client.get_channel(CHANNEL_ID)

    while True:
        if last_message:
            try:
                await last_message.delete()
            except:
                pass

        xml_data = fetch_vehicles_xml()
        if xml_data:
            lines = parse_vehicles(xml_data)
        else:
            lines = ["❌ Не удалось получить данные с FTP"]

        try:
            content = "\n".join(lines)
            last_message = await channel.send(content[:2000])
        except Exception as e:
            print(f"Ошибка отправки: {e}")

        await asyncio.sleep(30)

client.run(TOKEN)
