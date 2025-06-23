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
    good_embeds = []
    bad_embeds = []
    try:
        root = ET.fromstring(xml_data)
        for vehicle in root.findall("vehicle"):
            if vehicle.attrib.get("farmId") != FARM_ID:
                continue

            name = vehicle.get("filename", "Неизвестно").split("/")[-1].replace(".xml", "")

            fuel_level = 0.0
            fuel_capacity = 1.0
            fuel_percent = 0.0
            dirt_percent = 0.0

            # Топливо
            fillUnit = vehicle.find("fillUnit")
            if fillUnit is not None:
                for unit in fillUnit.findall("unit"):
                    if unit.attrib.get("fillType") == "DIESEL":
                        try:
                            fuel_level = float(unit.attrib.get("fillLevel", 0))
                            fuel_capacity = float(unit.attrib.get("capacity", 1))
                            fuel_percent = fuel_level / fuel_capacity
                        except:
                            pass

            # Износ
            damage = "?"
            wearable = vehicle.find("wearable")
            if wearable is not None:
                try:
                    dmg = float(wearable.attrib.get("damage", 0))
                    damage = f"{dmg * 100:.2f}%"
                except:
                    damage = "?"

            # Грязь
            washable = vehicle.find("washable")
            if washable is not None:
                dirtNode = washable.find("dirtNode")
                if dirtNode is not None:
                    try:
                        dirt_percent = float(dirtNode.attrib.get("amount", 0))
                    except:
                        pass

            fuel_str = f"{fuel_level:.0f} л ({fuel_percent * 100:.0f}%)"
            dirt_str = f"{dirt_percent * 100:.2f}%"

            # Цвет embed: зелёный (0x2ECC71) если >50% топлива и <50% грязи
            if fuel_percent > 0.5 and dirt_percent < 0.5:
                color = 0x2ECC71  # зелёный
                embed_list = good_embeds
            else:
                color = 0xE74C3C  # красный
                embed_list = bad_embeds

            embed = discord.Embed(title=f"🚜 {name}", color=color)
            embed.add_field(name="Топливо", value=fuel_str, inline=True)
            embed.add_field(name="Износ", value=damage, inline=True)
            embed.add_field(name="Грязь", value=dirt_str, inline=True)
            embed_list.append(embed)
    except Exception as e:
        embed = discord.Embed(title="❌ Ошибка при разборе XML", description=str(e), color=0xFF0000)
        bad_embeds.append(embed)

    return good_embeds + bad_embeds

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
        embeds = []
        if xml_data:
            embeds = parse_vehicles(xml_data)
        else:
            embeds = [discord.Embed(title="❌ Не удалось подключиться к FTP", color=0xFF0000)]

        if embeds:
            for embed in embeds:
                try:
                    await channel.send(embed=embed)
                except Exception as send_err:
                    print(f"Ошибка при отправке: {send_err}")
        else:
            await channel.send("ℹ️ Нет техники для отображения.")

        await asyncio.sleep(60)

client.run(TOKEN)
