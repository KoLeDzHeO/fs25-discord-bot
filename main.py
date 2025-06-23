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
    except Exception as e:
        return None

def parse_vehicles(xml_data):
    results = []
    try:
        root = ET.fromstring(xml_data)
        for vehicle in root.findall("vehicle"):
            name = vehicle.get("filename", "Неизвестно").split("/")[-1].replace(".xml", "")
            fuel = vehicle.findtext("fuelFillLevel", default="?")
            damage = vehicle.findtext("damage", default="?")
            dirt = vehicle.findtext("dirtAmount", default="?")
            results.append(f"🚜 {name} — топливо: {fuel}, износ: {damage}, грязь: {dirt}")
    except Exception as e:
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
        await channel.send("\n".join(messages[:10]))  # максимум 10 строк
        await asyncio.sleep(300)  # каждые 5 минут

client.run(TOKEN)
