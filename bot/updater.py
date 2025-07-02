async def update_message(bot: discord.Client):
    await bot.wait_until_ready()
    channel = await bot.fetch_channel(config.channel_id)
    if channel is None:
        print("❌ Канал не найден!")
        return

    async with aiohttp.ClientSession() as session:
        while not bot.is_closed():
            stats_xml = await fetch_stats_xml(session)
            vehicles_xml = await fetch_api_file(session, "vehicles")
            economy_xml = await fetch_api_file(session, "economy")
            career_api = await fetch_api_file(session, "careerSavegame")    # <-- ДОБАВЬ ЭТУ СТРОКУ
            career_ftp = await fetch_file("careerSavegame.xml")
            farmland_ftp = await fetch_file("farmland.xml")

            print(f"[DEBUG] Статусы: stats={bool(stats_xml)}, vehicles={bool(vehicles_xml)}, economy={bool(economy_xml)}, careerAPI={bool(career_api)}, careerFTP={bool(career_ftp)}, farmlandFTP={bool(farmland_ftp)}")
            
            if all([stats_xml, vehicles_xml, economy_xml, career_api, career_ftp, farmland_ftp]):
                data = parse_all(
                    server_stats=stats_xml,
                    vehicles_api=vehicles_xml,
                    economy_api=economy_xml,
                    career_savegame_api=career_api,        # <-- И ЭТУ СТРОКУ
                    career_savegame_ftp=career_ftp,
                    farmland_ftp=farmland_ftp,
                )
                embed = build_embed(data)

                async for msg in channel.history(limit=None):
                    try:
                        await msg.delete()
                    except Exception as e:
                        print(f"[Discord] Не удалось удалить сообщение: {e}")

                await channel.send(embed=embed)
                print("[Discord] ✅ Embed успешно отправлен.")
            else:
                print("[DEBUG] Не все данные загружены, пропускаем обновление.")

            await asyncio.sleep(config.ftp_poll_interval)
