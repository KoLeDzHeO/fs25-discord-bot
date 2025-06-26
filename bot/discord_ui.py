import discord


def create_report_embed(content: str) -> discord.Embed:
    """Return a simple embed for vehicle reports."""
    return discord.Embed(description=content, colour=discord.Colour.green())
