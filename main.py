import os
import asyncio
import discord
import ftplib
import xml.etree.ElementTree as ET
from io import BytesIO
from collections import defaultdict
from vehicle_filter import get_info_by_key, get_icon_by_class, CATEGORY_ORDER

last_messages = []

# === CONFIG ===
TOKEN = os.getenv("DISCORD_TOKEN")
CHANNEL_ID = int(os.getenv("DISCORD_CHANNEL_ID"))
FTP_HOST = os.getenv("FTP_HOST")
FTP_PORT = int(os.getenv("FTP_PORT", "21"))
FTP_USER = os.getenv("FTP_USER")
FTP_PASS = os.getenv("FTP_PASS")
FTP_PATH = os.getenv("FTP_PATH")
FARM_ID = "1"

client = discord.Client(intents=discord.Intents.default())

SKIP_OBJECTS = {
    "eggBoxPallet", "cementBagsPallet", "bigBag_seeds", "bigBagHelm_fertilizer",
    "bigBag_fertilizer", "goatMilkCanPallet", "roofPlatesPallet",
    "cementBricksPallet", "cementBoxPallet"
}

async def fetch_vehicles_xml():
    def _download():
        with ftplib.FTP() as ftp:
            ftp.connect(FTP_HOST, FTP_PORT)
            ftp.login(FTP_USER, FTP_PASS)
            buffer = BytesIO()
            ftp.retrbinary(f"RETR {FTP_PATH}", buffer.write)
            buffer.seek(0)
            return buffer.getvalue()
    try:
        return await asyncio.to_thread(_download)
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

def format_line(name, dirt, damage, fuel, max_fuel):
    status = []
    if dirt > 0.05:
        status.append(f"грязь {int(dirt * 100)}%")
    if damage > 0.05:
        status.append(f"повреж. {int(damage * 100)}%")
    if max_fuel and fuel < 0.80 * max_fuel:
        status.append(f"топл. {int(fuel)}L")
    stat_str = ", ".join(status)
    return f"{name:<32} {stat_str}" if status else name

def parse_vehicles(xml_data):
    categories = defaultdict(list)
    critical = []
    try:
        root = ET.fromstring(xml_data)
        for vehicle in root.findall("vehicle"):
            if vehicle.attrib.get("farmId") != FARM_ID:
                continue
            filename_raw = vehicle.get("filename")
            if not filename_raw:
                continue
            filename = filename_raw.split("/")[-1].replace(".xml", "")
            if filename in SKIP_OBJECTS:
                continue

            dirt, damage, fuel = extract_vehicle_info(vehicle)
            info = get_info_by_key(filename)
            max_fuel = info.get("fuel_capacity") or 0

            if damage <= 0.05 and dirt <= 0.05 and (not max_fuel or fuel >= 0.8 * max_fuel):
                continue

            category = info.get("class") or "Разное"
            name = info.get("name") or filename
            line = format_line(name, dirt, damage, fuel, max_fuel)
            categories[category].append(line)

            if damage > 0.5 or dirt > 0.5 or (max_fuel and fuel < 0.3 * max_fuel):
                critical.append(line)
    except Exception as e:
        return [], [f"Ошибка разбора XML: {e}"]
    return critical, format_output(categories)

def format_output(groups):
    order_map = {name: idx for idx, name in enumerate(CATEGORY_ORDER)}
    sorted_items = sorted(
        groups.items(),
        key=lambda kv: (order_map.get(kv[0], len(CATEGORY_ORDER)), kv[0]),
    )
    result = []
    for cat, items in sorted_items:
        block = [f"{cat}:"]
        block.extend(items)
        result.append("\n".join(block))
    return result

def split_messages(lines, max_length=2000):
    blocks, current = [], ""
    for section in lines:
        if len(current) + len(section) + 2 > max_length:
            blocks.append(current.strip())
            current = ""
        current += section + "\n"
    if current.strip():
        blocks.append(current.strip())
    return blocks

@client.event
async def on_ready():
    print(f"Бот запущен как {client.user}")
    await start_reporting()



async def start_reporting():
    global last_messages
    channel = client.get_channel(CHANNEL_ID)

    if not channel:
        print(f"❌ Канал с ID {CHANNEL_ID} не найден! Проверь переменную DISCORD_CHANNEL_ID.")
        return
    else:
        print(f"✅ Канал найден: {channel.name} ({channel.id})")

    # Удаляем все предыдущие сообщения от бота
    async for msg in channel.history(limit=None):
        if msg.author == client.user:
            try:
                await msg.delete()
            except Exception as e:
                print(f"⚠️ Не удалось удалить сообщение: {e}")

    while True:
        for msg in last_messages:
            try:
                await msg.delete()
            except:
                pass
        last_messages.clear()

        xml_data = await fetch_vehicles_xml()
        if not xml_data:
            print("❌ Не удалось получить XML с FTP")
            await channel.send("❌ Не удалось подключиться к FTP")
            await asyncio.sleep(30)
            continue
        else:
            print("✅ XML получен")

        critical, lines = parse_vehicles(xml_data)
        if not lines and not critical:
            print("ℹ️ Нет техники для обслуживания")
            await channel.send("ℹ️ Нет техники для обслуживания")
            await asyncio.sleep(30)
            continue

        output_lines = []

        if critical:
            crit_block = [
                "Техника в критическом состоянии:",
            ]
            crit_block.extend(critical)
            output_lines.append("\n".join(crit_block))


        output_lines.extend(lines)

        for block in split_messages(output_lines):
            try:
                sent = await channel.send(block)
                last_messages.append(sent)
            except Exception as e:
                print(f"Ошибка отправки: {e}")

        await asyncio.sleep(600)

client.run(TOKEN)
