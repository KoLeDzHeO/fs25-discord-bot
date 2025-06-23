import os
import asyncio
import discord
from ftplib import FTP
import xml.etree.ElementTree as ET
from io import BytesIO

TOKEN = os.getenv("DISCORD_TOKEN")
CHANNEL_ID = int(os.getenv("DISCORD_CHANNEL_ID"))
FTP_HOST = os.getenv("FTP_HOST")
FTP_PORT = int(os.getenv("FTP_PORT", "21"))
FTP_USER = os.getenv("FTP_USER")
FTP_PASS = os.getenv("FTP_PASS")
FTP_PATH = os.getenv("FTP_PATH")
FARM_ID = "1"  # оставляем только свою ферму

intents = discord.Intents.default()
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
    except Exception:
        return None

def parse_vehicles(xml_data):
    results = []
    try:
        root = ET.fromstring(xml_data)
        for vehicle in root.findall("vehicle"):
            if vehicle.attrib.get("farmId") != FARM_ID:
                continue

            name = vehicle.get("filename", "Неизвестно").split("/")[-1].replace(".xml", "")
            fuel = vehicle.findtext("fuelFillLevel")
            damage = vehicle.findtext("damage")
            dirt = vehicle.findtext("dirtAmount")

            # Пропускаем, если всё пусто
            if fuel is None and damage is None and dirt is None:
                continue

            fuel_str = f"{float(fuel):.0f}%" if fuel else "?"
            damage_str = f"{float(damage)*100:.0f}%" if damage else "?"
            dirt_str = f"{float(dirt)*100:.0f}%" if dirt else "?"

            results.append(f"🚜 {name} — топливо: {fuel_str}, износ: {damage_str}, грязь: {dirt_str}")
    except Exception:
        results.append("❌ Ошибка при разборе XML.")
    return results

@client.event
async def on_ready():
    print(f"✅ Бот запущен как {client.user}")
    channel = client.get_channel(CHANNEL_ID)
    while True:
        xml_data = fetch_vehicles_xml()
        if xml_data:
            messages = parse_vehicles(xml_data)
        else:
            messages = ["❌ Не удалось подключиться к FTP."]
        await channel.send("\n".join(messages[:10]) if messages else "ℹ️ Нет техники для отображения.")
        await asyncio.sleep(300)

client.run(TOKEN)
