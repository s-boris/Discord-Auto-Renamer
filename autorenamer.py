import traceback

import re

from collections import Counter

from discord import Forbidden
from discord.ext import commands

##Configure the bot
description = '''Gamerbot available Commands: '''
bot = commands.Bot(command_prefix='!', description=description)

client_loop = bot.loop


@bot.event
async def on_ready():
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')


@bot.event
async def on_command_error(error, ctx):
    if isinstance(error, commands.NoPrivateMessage):
        await bot.send_message(ctx.message.author, 'This command cannot be used in private messages.')
    elif isinstance(error, commands.DisabledCommand):
        await bot.send_message(ctx.message.author, 'Sorry. This command is disabled and cannot be used.')
    elif isinstance(error, commands.CommandInvokeError):
        print('In {0.command.qualified_name}:'.format(ctx))
        traceback.print_tb(error.original.__traceback__)
        print('{0.__class__.__name__}: {0}'.format(error.original))


@bot.event
async def on_member_update(before, after):
    if before.game != after.game:
        if after.voice_channel:
            try:
                if not re.search(r'\(.*?\)', after.voice_channel.name):
                    if after.game:
                        print(after.display_name + " changed game status to " + after.game.name)
                        await bot.edit_channel(after.voice_channel, name=after.voice_channel.name + " (" + after.game.name + ")")
                        print("Changing channel name to: " + after.voice_channel.name + " (" + after.game.name + ")")
                    else:
                        print(after.display_name + " changed game status to none")
                        await bot.edit_channel(after.voice_channel, name=re.sub(r'\(.*?\)', '', after.voice_channel.name))
                else:
                    to_name = getMostPlayedGameInChannel(after.voice_channel)
                    if to_name:
                        await bot.edit_channel(after.voice_channel, name=re.sub(r'\(.*?\)', '(' + to_name + ')', after.voice_channel.name))
                        print("Changing channel game tag from " + after.voice_channel.name + " to (" + to_name + ")")
                    else:
                        await bot.edit_channel(after.voice_channel, name=re.sub(r'\(.*?\)', '', after.voice_channel.name))
                        print("Removing game tag from " + after.voice_channel.name + " because most played game is none")
            except Forbidden:
                print("Warning: Didn't have permission to change the channel name...")
        print(after.display_name + " changed game status to none")


@bot.event
async def on_voice_state_update(before, after):
    try:
        if not before.voice_channel and after.voice_channel:
            print(after.display_name + " joined voice channel: " + after.voice_channel.name)
            if after.game:
                # check if hasn't been named already
                if not re.search(r'\(.*?\)', after.voice_channel.name):
                    await bot.edit_channel(after.voice_channel, name=after.voice_channel.name + " (" + after.game.name + ")")
                    print("Changing channel name to: " + after.voice_channel.name + " (" + after.game.name + ")")
                else:
                    to_name = getMostPlayedGameInChannel(after.voice_channel)
                    if to_name:
                        await bot.edit_channel(after.voice_channel, name=re.sub(r'\(.*?\)', '(' + to_name + ')', after.voice_channel.name))
                        print("Changing channel name to: " + after.voice_channel.name + " (" + to_name + ")")
                    else:
                        await bot.edit_channel(after.voice_channel, name=re.sub(r'\(.*?\)', '', after.voice_channel.name))
                        print("Removing eventual game tag from channel " + before.voice_channel.name + " because most played game is none")

        elif before.voice_channel and after.voice_channel and before.voice_channel != after.voice_channel:
            print(after.display_name + " changed voice channel from " + before.voice_channel.name + " to " + after.voice_channel.name)
            # remove game from channel name when leaving it and if channel is empty (the brackets)
            if not before.voice_channel.voice_members:
                await bot.edit_channel(before.voice_channel, name=re.sub(r'\(.*?\)', '', before.voice_channel.name))
                print("Removing eventual game tag from empty channel " + before.voice_channel.name)
            else:
                # channel that has been left still has people in it. update the name
                to_name = getMostPlayedGameInChannel(before.voice_channel)
                if to_name:
                    if not re.search(r'\(.*?\)', before.voice_channel.name):
                        await bot.edit_channel(before.voice_channel, name=before.voice_channel.name + " (" + to_name + ")")
                        print("Changing channel name to " + before.voice_channel.name + " (" + to_name + ")")
                    else:
                        await bot.edit_channel(before.voice_channel, name=re.sub(r'\(.*?\)', '(' + to_name + ')', before.voice_channel.name))
                        print("Changing game tag from " + before.voice_channel.name + " to (" + to_name + ")")
                else:
                    await bot.edit_channel(before.voice_channel, name=re.sub(r'\(.*?\)', '', before.voice_channel.name))
                    print("Removing eventual game tag from channel " + before.voice_channel.name + " because most played game is none")

            # check if new one hasn't been named already
            if not re.search(r'\(.*?\)', after.voice_channel.name):
                if after.game:
                    await bot.edit_channel(after.voice_channel, name=after.voice_channel.name + " (" + after.game.name + ")")
                    print("Changing channel name to " + after.voice_channel.name + " (" + after.game.name + ")")
            else:
                to_name = getMostPlayedGameInChannel(after.voice_channel)
                if to_name:
                    await bot.edit_channel(after.voice_channel, name=re.sub(r'\(.*?\)', '(' + to_name + ')', after.voice_channel.name))
                    print("Changing game tag from channel " + after.voice_channel.name + " to (" + to_name + ")")
                else:
                    await bot.edit_channel(after.voice_channel, name=re.sub(r'\(.*?\)', '', after.voice_channel.name))
                    print("Removing eventual game tag from channel " + after.voice_channel.name + " because most played game is none")

        elif before.voice_channel and not after.voice_channel:
            print(after.display_name + " left voice channel: " + before.voice_channel.name)
            # remove game from channel name when leaving and empty (the brackets)
            if not before.voice_channel.voice_members:
                await bot.edit_channel(before.voice_channel, name=re.sub(r'\(.*?\)', '', before.voice_channel.name))
                print("Removing eventual game tag from channel " + before.voice_channel.name)
            else:
                to_name = getMostPlayedGameInChannel(before.voice_channel)
                if to_name:
                    if not re.search(r'\(.*?\)', before.voice_channel.name):
                        await bot.edit_channel(before.voice_channel, name=before.voice_channel.name + " (" + before.game.name + ")")
                        print("Changing channel name to " + before.voice_channel.name + " (" + to_name + ")")
                    else:
                        await bot.edit_channel(before.voice_channel, name=re.sub(r'\(.*?\)', '(' + to_name + ')', before.voice_channel.name))
                        print("Changing game tag from " + before.voice_channel.name + " to (" + to_name + ")")
                else:
                    await bot.edit_channel(before.voice_channel, name=re.sub(r'\(.*?\)', '', before.voice_channel.name))
                    print("Removing eventual game tag from channel " + before.voice_channel.name + " because most played game is none")
    except Forbidden:
        print("Warning: Didn't have permission to change the channel name...")


def getMostPlayedGameInChannel(channel):
    members = channel.voice_members
    gamelist = []

    for m in members:
        if m.game:
            gamelist.append(m.game.name)
    count = Counter(gamelist)

    first_most_common = None
    if count.most_common(2):
        first_most_common = count.most_common(2)[0]

    second_most_common = None
    if len(count.most_common(2)) > 1:
        second_most_common = count.most_common(2)[1]

    if second_most_common and first_most_common[1] == second_most_common[1]:
        return "different games"
    elif first_most_common:
        return first_most_common[0]
    else:
        return None


def startup():
    bot.run("your token here")


startup()
