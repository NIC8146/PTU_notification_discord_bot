from selenium import webdriver
from selenium.webdriver.firefox.options import Options
import discord
import shutil
from time import sleep
from os import listdir, remove, path,mkdir, getcwd, environ
from threading import *
import asyncio
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import config
from time import gmtime, strftime



intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)
started=False

# check weather directory to downloadd pdf is present
file_path = getcwd()+"/PTU_notify"
if path.isdir(file_path):
    shutil.rmtree(file_path)
    mkdir(file_path)
    pass
else:
    mkdir(file_path)

if not path.isfile("previousfile.txt"):
    with open("previousfile.txt","w") as f:
        f.write("abc")

with open("previousfile.txt","r") as f:
    previous_pdf_name_onsite =f.read()

channels_file = "channels.txt"

# Create file if file is not present
if not path.isfile(channels_file):
    with open(channels_file,"w"):
        pass

# Get all channels from file to a list
with open(channels_file,"r") as channelfile:
    server_channels = channelfile.read().splitlines()
server_channels = [int(i) for i in server_channels]

# Present working directoory
cwd = getcwd()

# Get the current value of PATH
current_path = environ.get('PATH', '')

# Append the directory to the PATH if it's not already there
if cwd not in current_path.split(":"):
    new_path = current_path + ":" + cwd
    environ['PATH'] = new_path


# webdriver options
options = Options()
options.add_argument("--headless")
options.set_preference("browser.download.folderList", 2)
options.set_preference("browser.download.dir", file_path)
options.set_preference("pdfjs.disabled", True)

driver = webdriver.Firefox(options=options)

def logs(log):
    with open("bot.log","a") as f:
         f.write(f"[+] {strftime('%Y-%m-%d %H:%M:%S', gmtime())} {log}\n")

# write to file
def write_to_file(server_channels,channels_file):
    with open(channels_file,"w") as channelfile:
        for x in server_channels:
            channelfile.write(str(x) + "\n")

# Download and upload pdf to discord channels
def download_pdf(loop,):
    while True:
        global previous_pdf_name_onsite
        ptuexam_url = "https://www.ptuexam.com/PublicAnnoucements"

        # visit site
        driver.get(ptuexam_url)
        html = driver.execute_script("return document.documentElement.outerHTML")

        # wait for text available on site and locate for css element
        element = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "#root > div:nth-child(2) > div > div > div:nth-child(1) > div > div > div.MuiBox-root.jss11 > div > div")))

        logs("page loaded....")
        # get pdf name text
        new_pdf_name_onsite = element.text

        # check for new pdf
        if previous_pdf_name_onsite != new_pdf_name_onsite:
            previous_pdf_name_onsite = new_pdf_name_onsite
            with open("previousfile.txt","w") as f:
                f.write(previous_pdf_name_onsite)


            # locate download item element
            download_element = driver.find_element(By.CSS_SELECTOR, "#root > div:nth-child(2) > div > div > div:nth-child(1) > div > div > div.MuiBox-root.jss12 > div > div.MuiGrid-root.right-align.MuiGrid-item.MuiGrid-grid-xs-12.MuiGrid-grid-sm-4 > span")
            # cick on element to download
            download_element.click()

            logs("pdf downloading....")

            # check for file in drive
            pdf_on_drive = listdir(file_path)

            # wait for file to be downloaded if not downloaded yet
            while pdf_on_drive == []:
                sleep(5)
                pdf_on_drive = listdir(file_path)
            logs("pdf downloaded")

            # upload pdf to channels
            for x in server_channels[:]:
                with open(f"PTU_notify/{pdf_on_drive[0]}", 'rb') as f:
                    try:
                        channel_by_ID = client.get_channel(x)
                        coro = channel_by_ID.send(f"{previous_pdf_name_onsite}",file=discord.File(f))
                        future = asyncio.run_coroutine_threadsafe(coro, loop)
                        future.result()
                    except:
                        try:
                            server_channels.remove(x)
                        except:
                            pass    
            sleep(5)

            # delete pdf from drive
            remove(f"{file_path}/{pdf_on_drive[0]}")
            logs("new file sent")
        else:
            logs("present") 
        # sleep 12 hours
        sleep(43200)

@client.event
async def on_ready():
    logs(f'We have logged in as {client.user}')


@client.event
async def on_message(message):
    global started
    if message.author == client.user:
        return

    if message.content.startswith('!!help'):
        a = discord.Embed(color=0x3F9FFF, title="HELP", type='rich', description="discription of all commands\n")
        a.add_field(name="!!help", value="for help", inline=False)
        a.add_field(name="!!setup_ptu", value="To start notification on channel\nsend '!!setup_ptu' to channel on which you want to receive notifications/pdf", inline=False)
        a.add_field(name="!!remove", value="disable channel to get notifications\nsend '!!remove' to channel, that channel stop getting notifications/pdf", inline=False)
        a.add_field(name="!!disable", value="disable notification service for all channels of server", inline=False)
        await message.channel.send(embed=a)

    if message.content.startswith('!!remove'):
        text_channel_id = message.channel.id
        try:
            # delete channel from list
            remove(text_channel_id)

            # write new updated list to file
            write_to_file(server_channels,channels_file)
            await message.channel.send('PTU notifications stopped on this channel')
            logs("\033[0;31ma channel get removed\033[0m\n")
            logs(f"\033[0;32mTotal number of channels {len(server_channels)}\033[0m\n")
        except:
            await message.channel.send('This channel is not activated!!')

    if message.content.startswith('!!disable'):
        channels = message.guild.channels
        for channel in channels:
            try:
                server_channels.remove(channel.id)
            except:
                pass

        # write new updated list to file
        write_to_file(server_channels,channels_file)
        await message.channel.send('PTU notifications stoped on all channels of this server')
        logs("\033[0;31mA server disabled\033[0m\n")
        logs(f"\033[0;32mTotal number of channels {len(server_channels)}\033[0m\n")

    if message.content.startswith('!!setup_ptu'):
        text_channel_id = message.channel.id
        if text_channel_id not in server_channels:
            server_channels.append(text_channel_id)

            # write new updated list to file
            write_to_file(server_channels,channels_file)
            await message.channel.send('PTU notifications started on this channel')
            logs("\033[0;32mNew channel added\n")
            logs(f"Total number of channels {len(server_channels)}\033[0m\n")
        else:
            await message.channel.send('This channel already recives notification/pdf')

    if message.content.startswith('!!start_ptu()'):
        if not started:
            loop = asyncio.get_running_loop()
            notification_start = Thread(target=download_pdf, args=(loop,))
            notification_start.start()
            logs("run_ptu")
            started=True
        else:
            logs(f"\033[0;31mAlready started\033[0m\n")

try:
    client.run(config.token)
except Exception as e:
    if "Cannot connect to host discord.com" in str(e):
        logs("check your internet connection\n")
    else:
        logs(e)
    driver.close()

