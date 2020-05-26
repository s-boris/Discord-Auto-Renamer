# Discord auto-channel-renamer bot

A Discord bot that adds the currently most played game of the users inside a voice channel to the channel name.

## How to install:
- Run ``pip install discord.py --upgrade``
- Set the bot token at the bottom of the file
- Run the bot with `python autorenamer.py`

## Notes:
- Don't forget to give the bot persmission to manage the channels.
- If you want to exclude a channel from being renamed, just remove the bots manage channel permission for that specific channel.
- If the bot sets the channel name like "xxx (different games)" it means that there is no most played game inside that channel but everyone plays something different