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
FARM_ID = "1"

intents = discord.Intents.default()
client = discord.Client(intents=intents)

last_message = None  # для хранения последнего сообщения

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

            # Топливо
            fuel = "?"
            fillUnit = vehicle.find("fillUnit")
            if fillUnit is not None:
                for unit in fillUnit.findall("unit"):
                    if unit.attrib.get("fillType") == "DIESEL":
                        try:
                            fuel_val = float(unit.attrib.get("fillLevel", 0))
                            fuel = f"{fuel_val:.0f} л"
                        except:
                            fuel = "?"

            # Износ
            damage = "?"
            wearable = vehicle.find("wearable")
            if wearable is not None:
                try:
                    dmg = float(wearable.attrib.get("damage", 0))
                    damage = f"{dmg * 100:.2f}%"
                except:
                    pass

            # Грязь
            dirt = "?"
            washable = vehicle.find("washable")
            if washable is not None:
                dirtNode = washable.find("dirtNode")
                if dirtNode is not None:
                    try:
                        amount = float(dirtNode.attrib.get("amount", 0))
                        dirt = f"{amount * 100:.2f}%"
                    except:
                        pass

            results.append(f"🚜 {name} — топливо: {fuel}, износ: {damage}, грязь: {dirt}")
    except Exception:
        results.append("❌ Ошибка при разборе XML.")
    return results

@client.event
async def on_ready():
    global last_message
    print(f"✅ Бот запущен как {client.user}")
    channel = client.get_channel(CHANNEL_ID)
    while True:
        xml_data = fetch_vehicles_xml()
        if xml_data:
            messages = parse_vehicles(xml_data)
        else:
            messages = ["❌ Не удалось подключиться к FTP."]

        try:
            if last_message:
                await last_message.delete()
            last_message = await channel.send("\n".join(messages[:10]) if messages else "ℹ️ Нет техники для отображения.")
        except Exception as e:
            print(f"❌ Ошибка при отправке или удалении сообщения: {e}")

        await asyncio.sleep(30)

client.run(TOKEN)
