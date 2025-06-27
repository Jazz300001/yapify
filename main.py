from asyncio import tasks
from datetime import time
import discord
from discord.ext import commands, tasks
import logging
import random
from dotenv import load_dotenv
import os
from discord import app_commands
import requests
import aiohttp
import json
import praw
import feedparser
import asyncio
from keep_alive import keep_alive
load_dotenv()
token  = os.getenv('DISCORD_TOKEN')
RED_ID = os.getenv('RED_ID')
RED_SECRET = os.getenv('RED_SECRET')
discwebhook = os.getenv("DISCWEBHOOK")
ytchannelids = ["UCVS0xBpOtXBAl12rdG67-OQ", "UCWJ2lWNubArHWmf3FIHbfcQ", "UCCkxMbfZ80VFwwiRlIG5P5g"]
allrss = []

for i in range(len(ytchannelids)):
    id = ytchannelids[i]
    rss = f"https://www.youtube.com/feeds/videos.xml?channel_id={id}"
    allrss.append(rss)
print(allrss)
discchannel = 376203676215148546

from discord.ext import commands
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix='/', intents=discord.Intents.all())

@bot.command()
async def ping(ctx):
    await ctx.send("Pong!")

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}!')
    try:
        synced = await bot.tree.sync()
        print(f'Synced {len(synced)} slash commands.')
    except Exception as e:
        print(f"Sync failed: {e}")
    ytcheck.start()

@tasks.loop(minutes=10)
async def ytcheck():
    lastvids = {}
    for rss in allrss:
        feed = feedparser.parse(rss)
        recent = feed.entries[0]
        print(recent)
        if lastvids.get(rss) != recent.id:
            lastvids[rss] = recent.id
            channel = bot.get_channel(discchannel)
            await channel.send(f"peep da vid-- {recent.title}\n{recent.link}")
        else:
            channel = bot.get_channel(discchannel)
            channel.send("nothing new yet")

@bot.event
async def on_member_join(member):
    await member.send(f"whip it out and spin it, {member.name}")

@bot.event
async def on_message(message):
    othpic = "https://tenor.com/view/funny-gif-2583399619372591816"
    print(othpic)
    if message.author == bot.user:
        return
    if "watch" in message.content.lower():
        await message.channel.send(f"{message.author.mention} aw hell nah he watchin??\n{othpic}")
    await bot.process_commands(message)

@bot.tree.command()
async def spitskyrim(interaction: discord.Interaction):
    file_path = os.path.join(os.path.dirname(__file__), 'skyrim_quotes.json')
    with open(file_path, 'r', encoding='utf-8') as f:
        lore_data = json.load(f)["quotes"]
    quote = random.choice(lore_data)
    await interaction.response.send_message(f"I used to be an adventurer like you until I took an arrow to the knee,\n{quote}")

@bot.tree.command()
async def spitsw(interaction: discord.Interaction):
    file_path = os.path.join(os.path.dirname(__file__), 'clone_wars_quotes.json')
    with open(file_path, 'r', encoding='utf-8') as f:
        lore_data = json.load(f)["quotes"]
    quote = random.choice(lore_data)
    await interaction.response.send_message(f"May the force be with you,\n{quote}")

@bot.tree.command()
async def spitoog(interaction: discord.Interaction):
    file_path = os.path.join(os.path.dirname(__file__), 'master_oogway_quotes.json')
    with open(file_path, 'r', encoding='utf-8') as f:
        lore_data = json.load(f)["quotes"]
    quote = random.choice(lore_data)
    await interaction.response.send_message(f"Inner peace 🙏,\n{quote}")


@bot.tree.command()
async def spitatla(interaction: discord.Interaction):
    file_path = os.path.join(os.path.dirname(__file__), 'avatar_quotes.json')
    with open(file_path, 'r', encoding='utf-8') as f:
        lore_data = json.load(f)["quotes"]

    quote_entry = random.choice(lore_data)
    quote_text = quote_entry["quote"]
    speaker = quote_entry["speaker"]

    await interaction.response.send_message(f'My cabbages!!!\n"{quote_text}"— {speaker}')


@bot.tree.command()
async def bother(interaction: discord.Interaction, user: discord.User):
    try:
        videos = [f for f in os.listdir("vids") if f.endswith(".mp4")]
        pick = random.choice(videos)
        video = os.path.join(f"vids", pick)
        file = discord.File(video, filename=pick)
        await user.send(f"This was not sent to bother you,",file = file)
        await interaction.response.send_message("No I cant laugh yet, Ive got to hold it in", ephemeral=True)
    except discord.Forbidden:
        await interaction.response.send_message("dm forbidden bro think he mysterious", ephemeral=True)





@bot.tree.command()
async def racist(interaction: discord.Interaction):
    gif_url = "https://cdn.discordapp.com/attachments/1202760576300879964/1379988483707502602/IMG_6057.png?ex=684e1b6d&is=684cc9ed&hm=996d7a5c20dd75642087b455863f35a8134c00b6b88001e57c40a4964296fdd8&"
    await interaction.response.send_message(gif_url)

@bot.tree.command()
async def pinned(interaction: discord.Interaction):
    pins = await interaction.channel.pins()
    if not pins:
        await interaction.response.send_message("No pinned messages found.")
        return
    pin = random.choice(pins)
    embed = discord.Embed(
        description=pin.content or "No text content",
        timestamp=pin.created_at,
        color=discord.Color.blurple()
    )
    embed.set_author(name=pin.author.display_name, icon_url=pin.author.display_avatar.url)
    embed.add_field(name="Jump to Message", value=f"[Click here to view original]({pin.jump_url})", inline=False)
    if pin.attachments:
        embed.set_image(url=pin.attachments[0].url)
    await interaction.response.send_message(embed=embed)


reddit = praw.Reddit(
    client_id=RED_ID,
    client_secret = RED_SECRET,
    user_agent = "discord bot by /u/Ok-Walk1768"
)
@bot.tree.command()
async def red(interaction: discord.Interaction, sub:str, sort:str = "hot", numofposts:str = "3"):
    await interaction.response.defer()
    try:
        sub = reddit.subreddit(sub)
        if sort == "hot":
            posts = sub.hot(limit = int(numofposts))
        elif sort == "top":
            posts = sub.top(limit = int(numofposts))
        elif sort == "new":
            posts = sub.new(limit = int(numofposts))
        else:
            await interaction.followup.send(f"Sorry, {sort} isn't a valid sort.")
            return
        embeds = []

        for post in posts:
            embed = discord.Embed(
                title=post.title[:256],
                url=f"https://reddit.com{post.permalink}",
                description=f"👍 {post.score} | 💬 {post.num_comments}",
                color=discord.Color.blurple()
            )
            if post.selftext:
                text = post.selftext[:500] + "..." if len(post.selftext) > 500 else post.selftext
                embed.add_field(name="Post", value=text, inline=False)
            if hasattr(post, "post_hint") and post.post_hint == "image":
                embed.set_image(url=post.url)
            elif hasattr(post, "preview"):
                images = post.preview.get("images")
                if images:
                    image_url = images[0]["source"]["url"]
                    embed.set_image(url=image_url.replace("&amp;", "&"))

            embeds.append(embed)

        for embed in embeds:
            await interaction.followup.send(embed=embed)
    except Exception as e:
        print(e)
        await interaction.followup.send("An error occurred while fetching the posts.")


bot.run(token, log_handler=handler, log_level=logging.DEBUG)
