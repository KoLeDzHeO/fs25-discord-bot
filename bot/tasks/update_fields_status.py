import discord
from modules.fields import parse_field_statuses
from config import config
from utils.message_tracker import get_id, set_id

async def update_fields_status(client, ftp_client):
    """
    Обновляет или создаёт сообщение со статусом полей
    """
    try:
        # Загружаем данные полей
        xml_bytes = await ftp_client.fetch_fields_file()
        statuses = parse_field_statuses(xml_bytes)
        if not statuses:
            print("[Поля] Нет доступных полей для отображения.")
            return

        # Берём только первую страницу (до 25 строк)
        chunk = statuses[:25]
        embed = discord.Embed(title="🗺️ Статус полей", color=0x27ae60)
        for line in chunk:
            embed.add_field(name="\u200b", value=line, inline=False)

        # Получаем канал и ID старого сообщения
        channel = await client.fetch_channel(int(config.DISCORD_CHANNEL_ID))
        # Используем tracker для сохранения ID поля
        message_id = get_id("fields_message_id")

        if message_id:
            try:
                message = await channel.fetch_message(int(message_id))
                await message.edit(embed=embed)
                print("[Поля] Сообщение успешно обновлено.")
                return
            except discord.NotFound:
                print("[Поля] Старое сообщение не найдено, создаём новое...")

        # Если ID нет или сообщение удалено — создаём новое
        new_message = await channel.send(embed=embed)
        set_id("fields_message_id", new_message.id)
        print("[Поля] Создано новое сообщение для статуса полей.")

    except Exception as e:
        print(f"[Поля] Ошибка обновления: {e}")

