import discord
from discord.ext import commands
from dotenv import load_dotenv
import os

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')


class InviteButton(discord.ui.View):
    def __init__(self, link: str):
        super().__init__()
        self.link = link
        self.add_item(discord.ui.Button(label='Invite link', url=self.link))
    
    @discord.ui.button(label='Invite', style=discord.ButtonStyle.blurple)
    async def invite(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message(self.link, ephemeral=True)

@bot.command()
async def invite(ctx: commands.Context):
    # link = await ctx.channel.create_invite()
    link = 'https://discord.com/api/oauth2/authorize?client_id=1127887065246347366&permissions=1099511627776&scope=bot'
    await ctx.send('Click to invite', view=InviteButton(str(link)))

bot.run(TOKEN) # type: ignore
