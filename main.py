import os
from dotenv import load_dotenv
import discord
from discord.ext import commands, tasks
import json
import asyncio
import math
import random
from colorama import Fore, Style
from typing import List
from collections import deque
from itertools import cycle

load_dotenv()

TOKEN = os.getenv("TOKEN")

if TOKEN is None:
    raise ValueError("TOKEN not found in .env file. Please add it.")

bot = commands.Bot(command_prefix='.', intents=discord.Intents.all())
bot.remove_command('help')

statuses = cycle([
    discord.Activity(type=discord.ActivityType.watching, name="GBOTS"),
    discord.Game(name="GBOTS 🔛🔝"),
    discord.Activity(type=discord.ActivityType.listening, name=".help"),
    discord.Game(name="IM PUBLIC SO ADD ME") # Change this to whatever you want
])

@bot.event
async def on_ready():
    print_servers()
    print_info()
    change_status.start()

def print_servers():
    print(f'{Fore.CYAN}{Style.BRIGHT}♦═════════════════════ SERVERS LIST ═════════════════════♦{Style.RESET_ALL}')
    for guild in bot.guilds:
        print(f"{Style.BRIGHT}> {guild.name}  |  ID: {guild.id}{Style.RESET_ALL}")
    print(f"\n{Fore.CYAN}{Style.BRIGHT}Servers: {len(bot.guilds)}{Style.RESET_ALL}")

def print_info():
    command_count = sum(1 for command in bot.commands if not command.hidden)
    print(f'{Fore.CYAN}{Style.BRIGHT}♦═══════════════════════ INFO ════════════════════════════♦{Style.RESET_ALL}')
    print(f'{Fore.GREEN}  • The bot is Online!{Style.RESET_ALL}')
    print(f'{Fore.GREEN}  • Registered Commands: {command_count}{Style.RESET_ALL}')
    print(f'{Fore.GREEN}  • Made by MANNY1_.{Style.RESET_ALL}')
    print(f'{Fore.GREEN}  • Status: Watching GBOTS{Style.RESET_ALL}')
    print(f'{Fore.CYAN}{Style.BRIGHT}♦════════════════════════════════════════════════════════♦{Style.RESET_ALL}') # Change this to whatever aswell

@tasks.loop(seconds=5)
async def change_status():
    status = next(statuses)
    await bot.change_presence(activity=status)

# LEVEL SYS
allowed_user_ids = {1143551190731333662, 1166671317915938868, } # Add more if needed (change the user ids)

try:
    with open("users.json", "r") as users_file:
        users = json.load(users_file)
except FileNotFoundError:
    users = {}

async def save():
    await bot.wait_until_ready()
    while not bot.is_closed():
        with open("users.json", "w") as f:
            json.dump(users, f, indent=4)

        await asyncio.sleep(5)

def level_up(author_id):
    if author_id not in users:
        users[author_id] = {"Level": 1, "XP": 0}

    current_xp = users[author_id]["XP"]
    current_level = users[author_id]["Level"]

    if current_xp >= math.ceil((6 * (current_level) ** 4) / 2.5):
        users[author_id]["Level"] += 1
        return True
    else:
        return False

@bot.event
async def on_message(message):
    if message.author.bot:
        return

    author_id = str(message.author.id)

    if author_id not in users:
        users[author_id] = {"Level": 1, "XP": 0}

    random_xp = random.randint(5, 15)
    users[author_id]["XP"] += random_xp

    if level_up(author_id):
        level_up_embed = discord.Embed(title="You leveled up!", color=discord.Color.blurple())
        level_up_embed.add_field(name="Congrats", value=f"{message.author.mention} has just leveled up to level {users[author_id]['Level']}!!! Current XP: {users[author_id]['XP']}")

        await message.channel.send(embed=level_up_embed)

    await bot.process_commands(message)

@bot.command(aliases=["rank", "lvl"])
async def level(ctx, user: discord.User = None):
    user = user or ctx.author
    user_id = str(user.id)
    level_card = discord.Embed(title=f"{user.name}'s level & xp", color=discord.Color.random())
    level_card.add_field(name="Level", value=users.get(user_id, {}).get("Level", 1))
    level_card.add_field(name="XP", value=users.get(user_id, {}).get("XP", 0))
    level_card.set_footer(text=f"Requested by {ctx.author.name}", icon_url=ctx.author.avatar.url)

    await ctx.send(embed=level_card)

@bot.command(name='givexp', description='Give XP to yourself or other users')
async def give_xp(ctx, target: discord.Member, amount: int):
    if ctx.author.id not in allowed_user_ids:
        return await ctx.send("You do not have permission to use this command.")

    try:
        target_id = str(target.id)
        users[target_id]["XP"] += amount

        await ctx.send(f"Successfully gave {amount} XP to {target.display_name}.")
    
    except Exception as e:
        print(f"An error occurred: {e}")
        await ctx.send("An error occurred while processing the command.")

@bot.command(name='removexp', description='Remove XP from yourself or other users')
async def remove_xp(ctx, target: discord.Member, amount: int):
    if ctx.author.id not in allowed_user_ids:
        return await ctx.send("You do not have permission to use this command.")

    try:
        target_id = str(target.id)
        users[target_id]["XP"] -= amount

        await ctx.send(f"Successfully removed {amount} XP from {target.display_name}.")
    
    except Exception as e:
        print(f"An error occurred: {e}")
        await ctx.send("An error occurred while processing the command.")

@bot.command(name='leader', aliases=['top'], description='Show the top 10 users with the most XP and highest level')
async def leaderboard(ctx):
    sorted_users = sorted(users.items(), key=lambda x: x[1]["XP"], reverse=True)[:10]

    leaderboard_embed = discord.Embed(title='Leaderboard', color=discord.Color.gold())
    for i, (user_id, user_data) in enumerate(sorted_users, start=1):
        member = ctx.guild.get_member(int(user_id))
        leaderboard_embed.add_field(name=f"{i}. {member.display_name}" if member else f"{i}. Unknown User", value=f"Level: {user_data['Level']} | XP: {user_data['XP']}", inline=False)

    await ctx.send(embed=leaderboard_embed)



# eco commands
@bot.command(name='balance', description='Check yours or another user\'s balance')
async def balance(ctx, member: discord.Member=None):
    try:
        with open("eco.json", "r") as f:
            user_eco = json.load(f)

        if member is None:
            member = ctx.author

        user_id = str(member.id)

        if user_id not in user_eco:
            user_eco[user_id] = {}
            user_eco[user_id]["Balance"] = 100

            with open("eco.json", "w") as f:
                json.dump(user_eco, f, indent=4)

        eco_embed = discord.Embed(title=f"{member.name}'s Current Balance", description="The current balance of this user.", color=discord.Color.green())
        eco_embed.add_field(name="Current Balance:", value=f"${user_eco[user_id]['Balance']}.")
        eco_embed.set_footer(text="Want to increase your balance? Try running some of my economy commands!", icon_url=None)

        await ctx.send(embed=eco_embed)

    except Exception as e:
        print(f"An error occurred: {e}")

@commands.cooldown(1, 3600, commands.BucketType.user)
@bot.command(name='beg', description='Beg for more money!')
async def beg(ctx):
    with open("eco.json", "r") as f:
        user_eco = json.load(f)

    if str(ctx.author.id) not in user_eco:
        user_eco[str(ctx.author.id)] = {}
        user_eco[str(ctx.author.id)]["Balance"] = 100

        with open("eco.json", "w") as f:
            json.dump(user_eco, f, indent=4)

    cur_bal = user_eco[str(ctx.author.id)]["Balance"]
    amount = random.randint(0, 200)
    new_bal = cur_bal + amount

    user_eco[str(ctx.author.id)]["Balance"] = new_bal

    with open("eco.json", "w") as f:
        json.dump(user_eco, f, indent=4)

    if amount >= 0:
        eco_embed = discord.Embed(title="Oh nice you got money!", description="Some generous people gave you the most they could.", color=discord.Color.green())
        eco_embed.add_field(name="New balance:", value=f"${new_bal}", inline=False)
        eco_embed.set_footer(text="Want more? Wait 1 hour to run this command again, or try some other commands!", icon_url=None)
        await ctx.send(embed=eco_embed)

    else:
        eco_embed = discord.Embed(title="Oh No! - You've been ROBBED", description="A group of masked robbers saw you and took your money.", color=discord.Color.red())
        eco_embed.add_field(name="New balance:", value=f"${new_bal}", inline=False)
        eco_embed.set_footer(text="Maybe try begging in a nicer part of town next time...", icon_url=None)
        await ctx.send(embed=eco_embed)


@commands.cooldown(1, 3600, commands.BucketType.user)
@bot.command(name='work', description='Get a job for some quick money')
async def work(ctx):
    with open("eco.json", "r") as f:
        user_eco = json.load(f)

        if str(ctx.author.id) not in user_eco:
            user_eco[str(ctx.author.id)] = {}
            user_eco[str(ctx.author.id)]["Balance"] = 100

            with open("eco.json", "w") as f:
                json.dump(user_eco, f, indent=4)

        amount = random.randint(250, 800)
        user_eco[str(ctx.author.id)]["Balance"] += amount

        eco_embed = discord.Embed(title="Phew!", description="After a tiring shift here's what you earned..", color=discord.Color.green())
        eco_embed.add_field(name="Earnings:", value=f"${amount}", inline=False)
        eco_embed.add_field(name="New balance:", value=f"{user_eco[str(ctx.author.id)]['Balance']}")
        eco_embed.set_footer(text="Want more? Wait 1 hour to run this command again, or try some other commands!")
        await ctx.send(embed=eco_embed)

        with open("eco.json", "w") as f:
            json.dump(user_eco, f, indent=4)

@bot.command(name='deposit', aliases=['dp'], description='Deposit money to your bank')
async def deposit(ctx, amount: int):
    try:
        with open("eco.json", "r") as f:
            user_eco = json.load(f)

        user_id = str(ctx.author.id)

        if user_id not in user_eco:
            await ctx.send("You don't have an account. Use the `beg` command to get started.")
            return

        balance = user_eco[user_id]["Balance"]

        if amount <= 0:
            await ctx.send("Invalid deposit amount. Please enter a positive value.")
            return

        if balance < amount:
            await ctx.send("You don't have enough money to deposit.")
            return

        user_eco[user_id]["Balance"] -= amount
        user_eco[user_id]["Bank"] = user_eco.get(user_id, {}).get("Bank", 0) + amount

        with open("eco.json", "w") as f:
            json.dump(user_eco, f, indent=4)

        deposit_embed = discord.Embed(
            title="Deposit",
            description=f"You have successfully deposited ${amount} to your bank.",
            color=discord.Color.green()
        )
        await ctx.send(embed=deposit_embed)

    except Exception as e:
        print(f"An error occurred: {e}")

@bot.command(name='withdraw', aliases=['wd'], description='Withdraw money from your bank')
async def withdraw(ctx, amount: int):
    try:
        with open("eco.json", "r") as f:
            user_eco = json.load(f)

        user_id = str(ctx.author.id)

        if user_id not in user_eco:
            await ctx.send("You don't have an account. Use the `beg` command to get started.")
            return

        balance = user_eco[user_id]["Balance"]
        bank_balance = user_eco.get(user_id, {}).get("Bank", 0)

        if amount <= 0:
            await ctx.send("Invalid withdrawal amount. Please enter a positive value.")
            return

        if bank_balance < amount:
            await ctx.send("You don't have enough money in your bank to withdraw.")
            return

        user_eco[user_id]["Balance"] += amount
        user_eco[user_id]["Bank"] -= amount

        with open("eco.json", "w") as f:
            json.dump(user_eco, f, indent=4)

        withdraw_embed = discord.Embed(
            title="Withdraw",
            description=f"You have successfully withdrawn ${amount} from your bank.",
            color=discord.Color.gold()
        )
        await ctx.send(embed=withdraw_embed)

    except Exception as e:
        print(f"An error occurred: {e}")


@bot.command(name='lb', aliases=['leaderboard'], description='View the leaderboard')
async def leaderboard(ctx):
    try:
        with open("eco.json", "r") as f:
            user_eco = json.load(f)

        
        top_users = sorted(user_eco.items(), key=lambda x: x[1]["Balance"], reverse=True)[:10]

        lb_embed = discord.Embed(
            title="Leaderboard",
            color=discord.Color.gold()
        )

        for rank, (user_id, data) in enumerate(top_users, start=1):
            member = ctx.guild.get_member(int(user_id))
            lb_embed.add_field(
                name=f"#{rank} - {member.display_name if member else 'Unknown User'}",
                value=f"Balance: ${data['Balance']}",
                inline=False
            )

        await ctx.send(embed=lb_embed)

    except Exception as e:
        print(f"An error occurred: {e}")

allowed_user_ids = {1143551190731333662, 1166671317915938868} # Change these to whatever and add more if needed

@bot.command(name='givemoney', aliases=['give', 'grant'], description='Give money to yourself or other users')
async def give_money(ctx, target: discord.Member, amount: int):
    if ctx.author.id not in allowed_user_ids:
        return await ctx.send("You do not have permission to use this command.")

    try:
        with open("eco.json", "r") as f:
            user_eco = json.load(f)

        author_id = str(ctx.author.id)
        target_id = str(target.id)

        if author_id not in user_eco:
            user_eco[author_id] = {"Balance": 100}

        if target_id not in user_eco:
            user_eco[target_id] = {"Balance": 100}

        user_eco[author_id]["Balance"] -= amount
        user_eco[target_id]["Balance"] += amount

        with open("eco.json", "w") as f:
            json.dump(user_eco, f, indent=4)

        await ctx.send(f"Successfully gave {amount} money to {target.display_name}.")
    
    except Exception as e:
        print(f"An error occurred: {e}")
        await ctx.send("An error occurred while processing the command.")

@bot.command(name='removemoney', aliases=['remove', 'deduct'], description='Remove money from yourself or other users')
async def remove_money(ctx, target: discord.Member, amount: int):
    if ctx.author.id not in allowed_user_ids:
        return await ctx.send("You do not have permission to use this command.")

    try:
        with open("eco.json", "r") as f:
            user_eco = json.load(f)

        author_id = str(ctx.author.id)
        target_id = str(target.id)

        if author_id not in user_eco:
            user_eco[author_id] = {"Balance": 100}

        if target_id not in user_eco:
            user_eco[target_id] = {"Balance": 100}

        user_eco[author_id]["Balance"] -= amount
        user_eco[target_id]["Balance"] -= amount

        with open("eco.json", "w") as f:
            json.dump(user_eco, f, indent=4)

        await ctx.send(f"Successfully removed {amount} money from {target.display_name}.")
    
    except Exception as e:
        print(f"An error occurred: {e}")
        await ctx.send("An error occurred while processing the command.")


# HELP
@bot.command(name='help', aliases=['commands'])
async def help_command(ctx):
    prefix = "."

    economy_commands = [
        {"name": "work", "help": "Do some work to earn money!"},
        {"name": "beg", "help": "Beg people for some money!"},
        {"name": "balance", "help": "View your current balance"},
        {"name": "leaderboard", "help": "View the top 10 leaderboard"},
        {"name": "withdraw", "help": "Withdraw your money"},
        {"name": "deposit", "help": "Deposit your money"}
    ]

    level_commands = [
        {"name": "lvl", "help": "View your current level and xp"},
        {"name": "rank", "help": "Same as lvl 😀"},
        {"name": "top", "help": "View the top 10 level lb"}
    ]

    moderation_commands = [
        {"name": "kick", "help": "Kick a member from the server"},
        {"name": "ban", "help": "Ban a member from the server"},
        {"name": "unban", "help": "Unban a member from the server"},
        {"name": "mute", "help": "Mute a member"},
        {"name": "unmute", "help": "Unmute a member"},
        {"name": "setjoinchannel", "help": "Sets the join channel for when members join"},
        {"name": "setleavechannel", "help": "Sets the leave channel for when members join"},
        {"name": "addrole", "help": "Add roles to a user"},
        {"name": "removerole", "help": "Removes a role from a user"}
    ]

    utility_commands = [
        {"name": "serverinfo", "help": "View the server information"},
        {"name": "userinfo", "help": "View a users information"},
        {"name": "av", "help": "Get a users avatar picture"},
        {"name": "addme", "help": "Get the invite link for the bot"}
    ]

    embed = discord.Embed(
        title="Available Commands",
        color=discord.Color.blue()
    )

    if economy_commands:
        economy_list = "\n".join([f"`{prefix}{cmd['name']}` - {cmd['help']}" for cmd in economy_commands])
        embed.add_field(name="Economy Commands", value=economy_list, inline=False)

    if level_commands:
        level_list = "\n".join([f"`{prefix}{cmd['name']}` - {cmd['help']}" for cmd in level_commands])
        embed.add_field(name="Level Commands", value=level_list, inline=False)

    if moderation_commands:
        moderation_list = "\n".join([f"`{prefix}{cmd['name']}` - {cmd['help']}" for cmd in moderation_commands])
        embed.add_field(name="Moderation Commands", value=moderation_list, inline=False)

    if utility_commands:
        utility_list = "\n".join([f"`{prefix}{cmd['name']}` - {cmd['help']}" for cmd in utility_commands])
        embed.add_field(name="Utility Commands", value=utility_list, inline=False)

    await ctx.send(embed=embed)

# JOIN & LEAVE
try:
    with open("channel_settings.json", "r") as f:
        channel_settings = json.load(f)
except FileNotFoundError:
    channel_settings = {"join_channels": {}, "leave_channels": {}}

@bot.event
async def on_member_join(member):
    guild_id = str(member.guild.id)
    join_channel_id = channel_settings["join_channels"].get(guild_id)

    if join_channel_id:
        join_channel = member.guild.get_channel(join_channel_id)
        if join_channel:
            embed = discord.Embed(
                title=f"Welcome to the server, {member.name}!",
                description=f"Feel free to explore and enjoy your stay.",
                color=discord.Color.green()
            )
            await join_channel.send(embed=embed)

@bot.event
async def on_member_remove(member):
    guild_id = str(member.guild.id)
    leave_channel_id = channel_settings["leave_channels"].get(guild_id)

    if leave_channel_id:
        leave_channel = member.guild.get_channel(leave_channel_id)
        if leave_channel:
            embed = discord.Embed(
                title=f"Goodbye, {member.name}!",
                description=f"We'll miss you. Take care!",
                color=discord.Color.red()
            )
            await leave_channel.send(embed=embed)

@bot.command(name="setjoinchannel")
async def set_join_channel(ctx, channel: discord.TextChannel):
    if "join_channels" not in channel_settings:
        channel_settings["join_channels"] = {}
    channel_settings["join_channels"][str(ctx.guild.id)] = channel.id
    save_channel_settings()
    embed = discord.Embed(
        title="Join Channel Set",
        description=f"Join messages will now be sent in {channel.mention}.",
        color=discord.Color.blue()
    )
    await ctx.send(embed=embed)

@bot.command(name="setleavechannel")
async def set_leave_channel(ctx, channel: discord.TextChannel):
    if "leave_channels" not in channel_settings:
        channel_settings["leave_channels"] = {}
    channel_settings["leave_channels"][str(ctx.guild.id)] = channel.id
    save_channel_settings()
    embed = discord.Embed(
        title="Leave Channel Set",
        description=f"Leave messages will now be sent in {channel.mention}.",
        color=discord.Color.blue()
    )
    await ctx.send(embed=embed)

def save_channel_settings():
    with open("channel_settings.json", "w") as f:
        json.dump(channel_settings, f)

# MODERATION
@bot.command()
@commands.has_permissions(kick_members=True)
async def kick(ctx, user: discord.Member, *, reason="No reason given"):
    try:
        await user.kick(reason=reason)
        embed = discord.Embed(
            color=discord.Color.red(),
            title="Member Kicked",
            description=f"{user.mention} has been kicked from the server."
        )
        embed.add_field(name="Reason:", value=reason, inline=False)
        embed.set_footer(text=f"Kicked by {ctx.author.name}", icon_url=ctx.author.avatar.url)
        await ctx.send(embed=embed)

    except discord.Forbidden:
        await ctx.send("I don't have permission to kick members.")

    except discord.HTTPException as e:
        await ctx.send(f"An error occurred: {e}")

@kick.error
async def kick_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("You don't have permission to use this command.")
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("Please provide the member you want to kick.")
    else:
        await ctx.send(f"An error occurred: {error}")

@bot.command()
@commands.has_permissions(kick_members=True)
async def ban(ctx, user: discord.Member, *, reason="No reason given"):
    try:
        await user.ban(reason=reason)
        embed = discord.Embed(color=discord.Color.red(), title="User Banned", description=f"{user} has been banned from the server.")
        embed.add_field(name="Reason:", value=reason)
        await ctx.send(embed=embed)

    except Exception as e:
        print(f"An error occurred: {e}")

@bot.command()
@commands.has_permissions(ban_members=True)
async def unban(ctx, user: discord.User, *, reason="No reason given"):
    try:
        await ctx.guild.unban(user)
        embed = discord.Embed(color=discord.Color.green(), title="User Unbanned", description=f"{user} has been unbanned from the server.")
        embed.add_field(name="Reason:", value=reason)
        await ctx.send(embed=embed)

    except Exception as e:
        print(f"An error occurred: {e}")

@bot.command()
@commands.has_permissions(manage_roles=True)
async def mute(ctx, member: discord.Member, *, reason="No reason given"):
    try:
        muted_role = discord.utils.get(ctx.guild.roles, name="muted")

        if not muted_role:
            muted_role = await ctx.guild.create_role(name="muted")
            for channel in ctx.guild.channels:
                await channel.set_permissions(muted_role, send_messages=False)

        await member.add_roles(muted_role, reason=reason)
        embed = discord.Embed(color=discord.Color.orange(), title="User Muted", description=f"{member} has been muted.")
        embed.add_field(name="Reason:", value=reason)
        await ctx.send(embed=embed)

    except Exception as e:
        print(f"An error occurred: {e}")

@bot.command()
@commands.has_permissions(manage_roles=True)
async def unmute(ctx, member: discord.Member, *, reason="No reason given"):
    try:
        muted_role = discord.utils.get(ctx.guild.roles, name="muted")

        if not muted_role:
            raise commands.CommandError("Muted role not found. Please create a 'muted' role.")

        await member.remove_roles(muted_role, reason=reason)
        embed = discord.Embed(color=discord.Color.green(), title="User Unmuted", description=f"{member} has been unmuted.")
        embed.add_field(name="Reason:", value=reason)
        await ctx.send(embed=embed)

    except Exception as e:
        print(f"An error occurred: {e}")

@bot.command(name='addrole')
async def add_role(ctx, member: discord.Member, role: discord.Role):
    try:
        await member.add_roles(role)
        embed = discord.Embed(
            title="Role Added",
            description=f"The role {role.name} has been added to {member.mention}.",
            color=discord.Color.green()
        )
        await ctx.send(embed=embed)
    except Exception as e:
        print(f"An error occurred: {e}")

@bot.command(name='removerole')
async def remove_role(ctx, member: discord.Member, role: discord.Role):
    try:
        await member.remove_roles(role)
        embed = discord.Embed(
            title="Role Removed",
            description=f"The role {role.name} has been removed from {member.mention}.",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)
    except Exception as e:
        print(f"An error occurred: {e}")

# UTILITY
@bot.command()
async def serverinfo(ctx):
    info_embed = discord.Embed(title=f"Information about {ctx.guild.name}", description="All the information about the guild/server.", color=discord.Color.green())
    info_embed.set_thumbnail(url=ctx.guild.icon)
    info_embed.add_field(name="Name:", value=ctx.guild.name, inline=False)
    info_embed.add_field(name="ID:", value=ctx.guild.id, inline=False)
    info_embed.add_field(name="Owner:", value=ctx.guild.owner, inline=False)
    info_embed.add_field(name="Members:", value=ctx.guild.member_count, inline=False)
    info_embed.add_field(name="Channel Count:", value=len(ctx.guild.channels), inline=False)
    info_embed.add_field(name="Role Count:", value=len(ctx.guild.roles), inline=False)
    info_embed.add_field(name="Rules Channel:", value=ctx.guild.rules_channel, inline=False)
    info_embed.add_field(name="Booster Count:", value=ctx.guild.premium_subscription_count, inline=False)
    info_embed.add_field(name="Booster Tier:", value=ctx.guild.premium_tier, inline=False)
    info_embed.add_field(name="Created At:", value=ctx.guild.created_at.__format__("%A, %d. %B %Y @ %H:%M:%S "), inline=False)
    info_embed.set_footer(text=f"Requested by {ctx.author.name}", icon_url=ctx.author.avatar)

    await ctx.send(embed=info_embed)

@bot.command()
async def userinfo(ctx, member: discord.Member=None):
    if member is None:
        member = ctx.author
    elif member is not None:
        member = member

        info_embed = discord.Embed(title=f"Information about {ctx.guild.name}", description="All the information about the guild/server.", color=discord.Color.green())
        info_embed.set_thumbnail(url=member.avatar)
        info_embed.add_field(name="Name:", value=member.name, inline=False)
        info_embed.add_field(name="Nick Name:", value=member.display_name, inline=False)
        info_embed.add_field(name="Discriminator:", value=member.discriminator, inline=False)
        info_embed.add_field(name="ID:", value=member.id, inline=False)
        info_embed.add_field(name="Top Role:", value=member.top_role, inline=False)
        info_embed.add_field(name="Status:", value=member.status, inline=False)
        info_embed.add_field(name="Bot User?:", value=member.bot, inline=False)
        info_embed.add_field(name="Account Created", value=member.created_at.__format__("%A, %d %B %Y %H:%M:%S"), inline=False)
        info_embed.add_field(name="Joined Server", value=member.joined_at.__format__("%A, %d %B %Y %H:%M:%S"), inline=False)

        await ctx.send(embed=info_embed)

@bot.command()
async def av(ctx, member: discord.Member = None):
    if member is None:
        member = ctx.author
    embed = discord.Embed(title=f"{member.name}'s Avatar").set_image(url=member.avatar.url)
    await ctx.send(embed=embed)

@bot.command(name='invite', aliases=['invitelink', 'addme'])
async def invite_command(ctx):
    invite_link = "https://discord.com/api/oauth2/authorize?client_id=1187944228999934024&permissions=8&scope=bot" # Change to your bot invite or remove

    embed = discord.Embed(
        title="Invite the Bot",
        description="Click [here](" + invite_link + ") to invite me to your server!",
        color=discord.Color.blue()
    )

    await ctx.send(embed=embed, ephemeral=True)


bot.run(TOKEN)
