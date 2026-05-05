import asyncio

import discord

from load_json import add_data, channels

# Dictionnaire des actions disponibles
AVAILABLE_ACTIONS = {}


def register_action(action_name: str):
    """Décorateur pour enregistrer une action réutilisable."""
    def decorator(func):
        AVAILABLE_ACTIONS[action_name] = func
        return func
    return decorator


@register_action('lucky_gamble')
async def action_lucky_gamble(ctx, bot, user, item):
    """Action pour l'item chance au gamble."""
    user.set_enhanced_gambles(3)
    await ctx.send(item.achat)
    return True


@register_action('speak_message')
async def action_speak_message(ctx, bot, user, item):
    """Action pour faire parler le bot dans le général."""
    await ctx.send(item.achat)
    await ctx.author.send("Dis moi ce que tu veux que je dise dans le général")
    def check_msg(m):
        return m.author == ctx.author and m.guild is None

    try:
        message = await bot.wait_for('message', timeout=30.0, check=check_msg)
        general = discord.utils.get(ctx.guild.text_channels, id=channels["general"])
        if general:
            await general.send(message.content)
        await ctx.send("Message envoyé!")
        return True
    except asyncio.TimeoutError:
        await ctx.send("Trop lent, annulé !")
        return False


@register_action('teach_answer')
async def action_teach_answer(ctx, bot, user, item):
    """Action pour apprendre une nouvelle réponse au bot."""
    await ctx.send(item.achat)
    await ctx.author.send("Dis moi ce que tu veux que j'apprenne")

    def check_msg(m):
        return m.author == ctx.author and m.guild is None

    try:
        message = await bot.wait_for('message', timeout=30.0, check=check_msg)
        add_data(message.content, message.content, "answers.json")
        await ctx.send(f"J'ai appris: {message.content}")
        return True
    except asyncio.TimeoutError:
        await ctx.send("Trop lent, annulé !")
        return False


def get_action_by_name(action_name: str):
    """Récupère une fonction d'action par son nom."""
    return AVAILABLE_ACTIONS.get(action_name)


