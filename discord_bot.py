import discord
from discord.ext import commands
from koboldapp_interact import send_kobold_a_message
import re 

from config import TOKEN

# Define intents (needed for reading messages)
intents = discord.Intents.default()
intents.message_content = True  # allows the bot to read message content

# Create bot instance
bot = commands.Bot(command_prefix="!", intents=intents)

# Event: runs when bot is online
@bot.event
async def on_ready():
    print(f"Bot is online as {bot.user}")

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return  # ignore its own messages

    # Check if the bot is mentioned
    if bot.user in message.mentions:
        
        user_message = re.sub(f'<@!?{bot.user.id}>', '', message.content).strip()

        # Send cleaned message to KoboldAI
        bot_response = send_kobold_a_message(user_message)
        if ".png" in bot_response:
            embed = discord.Embed(description="Here's your image!")
            embed.set_image(url="attachment://output.png")
            await message.channel.send(embed=embed, file=discord.File(bot_response))
        else:
            await message.channel.send(f"{bot_response}")
    
    # Make sure commands still work
    await bot.process_commands(message)

# Command example: user types "!hello" in Discord
@bot.command()
async def hello(ctx):
    await ctx.send("Hello! I'm alive!")

# Start the bot
bot.run(TOKEN)
