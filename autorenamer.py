import traceback
import re
from collections import Counter
from discord import Forbidden
from discord.ext import commands

# Configure the bot
# --------------------------------------------
TOKEN = 'YourBotKey'
description = '''Channel renamer bot '''
bot = commands.Bot(command_prefix='!', description=description)


# --------------------------------------------


@bot.event
async def on_ready():
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')


@bot.event
async def on_command_error(error, ctx):
    if isinstance(error, commands.NoPrivateMessage):
        await ctx.send('This command cannot be used in private messages.')
    elif isinstance(error, commands.DisabledCommand):
        await ctx.send('Sorry. This command is disabled and cannot be used.')
    elif isinstance(error, commands.CommandInvokeError):
        print('In {0.command.qualified_name}:'.format(ctx))
        traceback.print_tb(error.original.__traceback__)
        print('{0.__class__.__name__}: {0}'.format(error.original))


@bot.event
async def on_member_update(before, after):
    if before.activities == after.activities:
        return

    if not after.voice:
        return

    await handle_game_activity_update(after, after.voice.channel)


@bot.event
async def on_voice_state_update(member, before, after):
    if before.channel:  # update the channel he just left
        await handle_game_activity_update(member, before.channel)

    if after.channel:  # update the channel he just joined
        await handle_game_activity_update(member, after.channel)


async def handle_game_activity_update(member, voice_channel):
    try:
        p = re.compile('(.*)\s\((.*?)\)')
        m = p.search(voice_channel.name)

        if not m:  # no game is set in the title
            if member.activity:  # is playing a game
                print(member.name + " changed activity status to " + member.activity.name)
                await voice_channel.edit(name="{} ({})".format(voice_channel.name, member.activity.name))
            else:  # is not playing a game anymore
                print(
                    "Warning: Someone changed from an activity to none but no channel game was set before.")
        else:  # a game is set in the title
            current_channel_name = m.group(1)
            current_channel_game = m.group(2)
            to_game = get_most_played_game_in_channel(voice_channel)
            if to_game:
                if not current_channel_game == to_game:
                    await voice_channel.edit(name="{} ({})".format(current_channel_name, to_game))
                    print("Updating channel {} game from {} to {}".format(current_channel_name, current_channel_game,
                                                                          to_game))
            else:  # nobody in the channel is playing a game anymore
                await voice_channel.edit(name=current_channel_name)
                print("Removing game from " + current_channel_name + " because most played game is none")
    except Forbidden:
        print("Warning: Didn't have permission to change the channel name")


def get_most_played_game_in_channel(channel):
    members = channel.members
    gamelist = []

    for m in members:
        if m.activity:
            gamelist.append(m.activity.name)
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


bot.run(TOKEN)
