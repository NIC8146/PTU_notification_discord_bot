
# PTU notification discord bot

PTU_notification_discord_bot is a discord bot as name suggests. It send announcements/notifications of PTU (Punjab Technical University) as a discord message.
## Clone
Clone the project

```bash
  git clone https://github.com/Nishant8146/Convac.git
```

Go to the project directory

```bash
  cd PTU_notification_discord_bot
```


## Requirments

To install required pakages, run following command.
```bash
pip install -r requirments.txt
```

## Bot Startup

Follow this link to make a discord bot accountand get token.
https://discordpy.readthedocs.io/en/stable/discord.html

Then invite bot to server and execute commands 

## Add bot account token
make a discord bot account, copy token then paste in **config.py** file.

## Usage

**Depending on os execute specific py file**

**For Windows**
```bash
  python discord_bot_windows.py
```

**For Linux**
```bash
  python discord_bot_linux.py
```
or
```bash
  python3 discord_bot_linux.py
```


## Bot commands on discord

* To show all commands
```bash
  !!help
```

* To start notification on channel
```bash
  !!setup_ptu
```

* Disable channel to get notifications
```bash
  !!remove
```

* Disable notification service for all channels of server
```bash
  !!disable
```

* To start bot on server **(only for administrator of bot)**
```bash
  !!start_ptu()
```
Bot does not start working until this command is not executed,this command does not showed in help message.
