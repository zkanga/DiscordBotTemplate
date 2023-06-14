from bot_utils.globals import logger, channel_name, bot, bot_roles, role_colors
from time import sleep
import discord
from discord.ext import commands


class BotNotifications(commands.Cog):
    def __init__(self):
        self.bot = bot

    @commands.command()
    async def roles(self, ctx):
        """Prints all roles available through me"""
        await ctx.send(f"The available roles are {bot_roles} \n{ctx.author.mention}")

    @commands.command()
    async def addRole(self, ctx, *, message):
        """Assign to yourself or another"""
        await role_command('add', ctx, message)

    @commands.command()
    async def dropRole(self, ctx, *, message):
        """Remove to yourself or another"""
        await role_command('remove', ctx, message)


async def role_command(cmd_type, ctx, message):
    if message in bot_roles:
        role_name = message
        assignee = ctx.author
    else:
        username = str(message).split(' ')[0]
        role_name = message[len(username) + 1:]
        assignee = discord.utils.find(
            lambda m: m.name == username or (m.nick and m.nick == username), ctx.guild.members
        )
    if role_name not in bot_roles:
        await ctx.send(f"That is not a role for this bot.\n{ctx.author}")
    if cmd_type == 'add':
        role = discord.utils.get(ctx.guild.roles, name=role_name)
        if role is None:
            await create_role(ctx.guild, role_name)
            role = discord.utils.get(ctx.guild.roles, name=role_name)
        await assignee.add_roles(role)
        logger.info(f"Role '{role_name}' added to {assignee}")
        await ctx.send(f"Role '{role_name}' added to {assignee.mention}")
    elif cmd_type == 'remove':
        role = discord.utils.get(ctx.guild.roles, name=role_name)
        if role is None:
            await create_role(ctx.guild, role_name)
            role = discord.utils.get(ctx.guild.roles, name=role_name)
        await assignee.remove_roles(role)
        logger.info(f"Role '{role_name}' removed from {assignee}")
        await ctx.send(f"Role '{role_name}' removed from {assignee.mention}")


async def create_channel(guild):
    # overwrites = {
    #     guild.default_role: discord.PermissionOverwrite(read_messages=False),
    #     guild.me: discord.PermissionOverwrite(read_messages=True)
    # }
    overwrites = {
        guild.default_role: discord.PermissionOverwrite(read_messages=True)
    }
    channel = await guild.create_text_channel(channel_name, overwrites=overwrites)
    sleep(5)
    logger.info(f"Created channel {channel.name} in guild {guild.name}")


async def create_role(guild, role_name):
    role = await guild.create_role(name=role_name, color=role_colors[bot_roles.index(role_name)])
    await role.edit(mentionable=True)
    sleep(5)
    logger.info(f"Created role {role.name} in guild {guild.name}")


async def ping_in_all_bot_commands(message, roles):
    for guild in bot.guilds:
        await ping_in_guild(guild, message, roles)


async def ping_in_guild(guild, message, roles):
    # Create the channel if it doesn't exist
    channel = discord.utils.get(guild.channels, name=channel_name)
    if not channel:
        await create_channel(guild)
        channel = discord.utils.get(guild.channels, name=channel_name)
    output = f"{message}\n"
    for role_name in roles:
        # Create the role if it doesn't exist
        curr_role = discord.utils.get(guild.roles, name=role_name)
        if not curr_role:
            await create_role(guild, role_name)
            curr_role = discord.utils.get(guild.roles, name=role_name)
        output += curr_role.mention
    await channel.send(output)


@bot.event
async def on_guild_join(guild):
    # Code to execute when the bot joins a new guild
    # You can perform tasks such as sending a welcome message, creating default channels, etc.
    # await guild.system_channel.send(f"Thank you for adding me, *{bot.user.name}* to your server!")
    await ping_in_guild(guild, f"{bot.user.name} is here and ready to Flamenco", bot_roles)
    logger.info(f'SUCCESS: Joined new guild - {guild}')


