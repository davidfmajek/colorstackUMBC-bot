"""
ColorStack@UMBC onboarding bot.

Flow: join (Verifying) -> Start button / name modal (Name Set) ->
rules checkmark (Rules Agreed) -> year role via Carl-bot -> intro
post (Intro Done) -> LinkedIn link (colorstackers).

Setup: create Verifying, Name Set, Rules Agreed, Intro Done (above
@everyone, below Admins). Fill CONFIG IDs. Gate each onboarding
channel to its step role; hide them from @everyone. Enable Server
Members + Message Content intents. Owner commands: !post_start,
!post_rules.
"""

import os
import re
import discord
from discord import app_commands
from discord.ext import commands

# ============ CONFIG - FILL THESE IN ============
GUILD_ID = 1537453892424564738  # ColorStack@UMBC

ROLE_VERIFYING = 1549830086809886721
ROLE_NAME_SET = 1549830229894107197
ROLE_RULES_AGREED = 1549830337306173460
ROLE_INTRO_DONE = 1549830367291252787
ROLE_COLORSTACKERS = 1542663349207048202
YEAR_ROLE_IDS = {
    1544355271676133437,  # Freshman
    1544355272833761442,  # Sophomore
    1544355273517572266,  # Junior
    1544355274612019282,  # Senior
    1544355275912515770,  # Alumni
}

CHANNEL_START_HERE = 1537453893322154164
CHANNEL_WELCOME_RULES = 1537453893322154165
CHANNEL_GET_ROLES = 1544355271504167012
CHANNEL_INTRODUCTIONS = 1537474373961912390
CHANNEL_LINKEDIN = 1545068257600344114

BOT_TOKEN = os.environ.get("DISCORD_BOT_TOKEN", "PASTE_YOUR_TOKEN_HERE")
# ==================================================

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)


# ---------- Step 1: assign Verifying role on join ----------
@bot.event
async def on_member_join(member: discord.Member):
    role = member.guild.get_role(ROLE_VERIFYING)
    if role:
        await member.add_roles(role, reason="New member - starting onboarding")


# ---------- Step 2: Start button -> Name modal ----------
class NameModal(discord.ui.Modal, title="Welcome to ColorStack@UMBC!"):
    first_name = discord.ui.TextInput(label="First Name", max_length=32)
    last_name = discord.ui.TextInput(label="Last Name", max_length=32)

    async def on_submit(self, interaction: discord.Interaction):
        member = interaction.user
        full_name = f"{self.first_name.value.strip()} {self.last_name.value.strip()}"

        try:
            await member.edit(nick=full_name)
        except discord.Forbidden:
            pass  # bot may lack permission to rename this member (e.g. server owner)

        guild = interaction.guild
        verifying = guild.get_role(ROLE_VERIFYING)
        name_set = guild.get_role(ROLE_NAME_SET)

        if verifying and verifying in member.roles:
            await member.remove_roles(verifying)
        if name_set:
            await member.add_roles(name_set)

        await interaction.response.send_message(
            f"Thanks {self.first_name.value}! Head to #welcome-and-rules next.",
            ephemeral=True,
        )


class StartView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Start", style=discord.ButtonStyle.success, custom_id="onboarding_start_btn")
    async def start_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(NameModal())


@bot.command()
@commands.has_permissions(administrator=True)
async def post_start(ctx: commands.Context):
    channel = bot.get_channel(CHANNEL_START_HERE)
    await channel.send(
        "**Welcome to ColorStack@UMBC!**\nClick below to get started.",
        view=StartView(),
    )
    await ctx.send("Posted.", delete_after=5)


# ---------- Step 3: rules message + checkmark reaction ----------
RULES_MESSAGE_ID = None  # filled in automatically when !post_rules runs


@bot.command()
@commands.has_permissions(administrator=True)
async def post_rules(ctx: commands.Context):
    global RULES_MESSAGE_ID
    channel = bot.get_channel(CHANNEL_WELCOME_RULES)
    msg = await channel.send(
        "React with ✅ once you've read the rules above to unlock #get-roles."
    )
    await msg.add_reaction("✅")
    RULES_MESSAGE_ID = msg.id
    await ctx.send(f"Posted. Message ID {msg.id} saved for this session.", delete_after=8)


@bot.event
async def on_raw_reaction_add(payload: discord.RawReactionActionEvent):
    if payload.channel_id != CHANNEL_WELCOME_RULES:
        return
    if str(payload.emoji) != "✅":
        return
    if RULES_MESSAGE_ID is not None and payload.message_id != RULES_MESSAGE_ID:
        return

    guild = bot.get_guild(payload.guild_id)
    member = guild.get_member(payload.user_id)
    if member is None or member.bot:
        return

    rules_agreed = guild.get_role(ROLE_RULES_AGREED)
    if rules_agreed and rules_agreed not in member.roles:
        await member.add_roles(rules_agreed)


# ---------- Step 4 (year roles) handled by Carl-bot already ----------

# ---------- Step 5: any message in #introductions -> Intro Done ----------
# ---------- Step 6: LinkedIn link in #linkedin -> colorstackers ----------
LINKEDIN_PATTERN = re.compile(r"linkedin\.com", re.IGNORECASE)


@bot.event
async def on_message(message: discord.Message):
    if message.author.bot:
        return

    if message.channel.id == CHANNEL_INTRODUCTIONS:
        member = message.author
        intro_done = message.guild.get_role(ROLE_INTRO_DONE)
        has_year_role = any(r.id in YEAR_ROLE_IDS for r in member.roles)
        if has_year_role and intro_done and intro_done not in member.roles:
            await member.add_roles(intro_done)
            try:
                await message.channel.send(
                    f"Thanks for the intro, {member.mention}! #linkedin is now unlocked.",
                    delete_after=15,
                )
            except discord.Forbidden:
                pass

    elif message.channel.id == CHANNEL_LINKEDIN:
        member = message.author
        colorstackers = message.guild.get_role(ROLE_COLORSTACKERS)
        if LINKEDIN_PATTERN.search(message.content) and colorstackers and colorstackers not in member.roles:
            await member.add_roles(colorstackers)
            try:
                await message.channel.send(
                    f"Welcome to the full server, {member.mention}! 🎉",
                    delete_after=15,
                )
            except discord.Forbidden:
                pass

    await bot.process_commands(message)


@bot.event
async def on_ready():
    print(f"Logged in as {bot.user} - onboarding bot is live.")


bot.run(BOT_TOKEN)