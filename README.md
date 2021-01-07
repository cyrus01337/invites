# Invites
### What is Invites? What does it do?
Invites is a small, easy to use cog for tracking which invites joining members use! It relies on a number of attributes added to your Bot for convenience as well as `on_invite_update` - a new, custom event that is dispatched

- Upon loading, assigns `Bot.invites`, `Bot.expiring_invites`, `Bot.shortest_invite`, `Bot.last_update`, `Bot.get_invite()` and `Bot.wait_for_invites()`
    - This is noted to reduce conflicts for developers utilising bot variables

- Requirements
    - discord.py 1.5.0+
    - GUILDS, SERVER_MEMBERS and INVITES intents
    - `manage_guild` and `manage_channels` permissions

### How do I use this?
1. Click on `invites.py` in the repository's file directory
![Screenshot](https://i.imgur.com/SsA8hQa.png)
2. Right-click the "Raw" button and click the "Save link as..." option
![Screenshot](https://i.imgur.com/kEFjCRj.png)
3. Save it within your cogs directory or wherever you store/load your cogs
![Screenshot](https://i.imgur.com/Q4I84pz.png)
4. Code away using the newly implemented features!
**NOTE: REMEMBER TO LOAD THE COG TO BE ABLE TO USE IT'S FEATURES**

### There is a problem with this, how can I report it?
There are two ways to report a problem:

1. Create an [issue](https://github.com/cyrus01337/invites/issues/new/choose) for this repository.
2. Ping me in the Discord.py server (Cyrus - `<@668906205799907348>`)

I (Cyrus) *personally* prefer and recommend the former but if I am around in **#help** or **#testing** then feel free to ping me in those respective channels.

### Is there any way for me to contribute?
Thank you in advance if you do choose to contribute - I am open to constructive criticism and will happily review any PRs sent to this repo!
