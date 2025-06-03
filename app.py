import discord
from discord.ext import commands
import asyncio
from keep_alive import keep_alive
from dotenv import load_dotenv
import os
# Set up the bot
bot = commands.Bot(command_prefix="$", intents=discord.Intents.all())

# Ticket category ID (replace with your category ID)
TICKET_CATEGORY_ID = 1379533806675169290 # Replace with your ticket category ID

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user.name}")

@bot.command()
async def ticket(ctx, *, issue=None):
    """Creates a new ticket."""

    guild = ctx.guild
    author = ctx.author

    # Check if a ticket channel already exists for the user
    existing_ticket = discord.utils.get(guild.channels, name=f"ticket-{author.name.lower()}")
    if existing_ticket:
        await ctx.send(f"You already have an open ticket at {existing_ticket.mention}!")
        return

    # Create the ticket channel
    category = bot.get_channel(TICKET_CATEGORY_ID)  # Get the ticket category
    if not isinstance(category, discord.CategoryChannel):
        await ctx.send("Invalid ticket category.  Please set the correct category ID.")
        return

    overwrites = {
        guild.default_role: discord.PermissionOverwrite(view_channel=False),
        author: discord.PermissionOverwrite(view_channel=True, send_messages=True, attach_files=True),
        guild.me: discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True)  # Bot permissions
    }

    try:
        channel = await category.create_text_channel(name=f"ticket-{author.name.lower()}", overwrites=overwrites, topic=f"Ticket created by {author.mention}. Issue: {issue}")
    except discord.errors.Forbidden:
        await ctx.send("I do not have the necessary permissions to create a channel in that category.")
        return
    except Exception as e:
        await ctx.send(f"An error occurred while creating the ticket: {e}")
        return

    # Send a message in the ticket channel
    embed = discord.Embed(title="Support Ticket", description=f"Thank you for creating a ticket!  Our support team will attend your ticket shortly.\n\n**Issue:** {issue or 'No issue specified.'}", color=discord.Color.green())
    embed.set_footer(text=f"Ticket created by {author.name}")
    await channel.send(author.mention, embed=embed)
    await ctx.send(f"Your ticket has been created at {channel.mention}!")
   


@bot.command()
@commands.has_permissions(manage_channels=True)
async def close(ctx, *, reason=None):
    """Closes the current ticket channel."""

    channel = ctx.channel
    if not channel.name.startswith("ticket-"):
        await ctx.send("This is not a ticket channel.")
        return

    # Archive the ticket (optional - requires setting up an archive category)
    # archive_category_id = 9876543210  # Replace with your archive category ID
    # archive_category = bot.get_channel(archive_category_id)
    # await channel.move(category=archive_category, end=True)

    embed = discord.Embed(title="Ticket Closed", description=f"This ticket has been closed by {ctx.author.mention}.\n\n**Reason:** {reason or 'No reason provided.'}", color=discord.Color.red())
    await channel.send(embed=embed)

    await channel.set_permissions(ctx.guild.default_role, view_channel=False) #Denies everyone to view the channel

    await asyncio.sleep(5) #Wait 5 seconds before deleting the channel

    await channel.delete(reason=reason)

@bot.command()
@commands.has_permissions(manage_channels=True)
async def adduser(ctx, user: discord.Member):
    """Adds a user to the ticket channel."""
    channel = ctx.channel
    if not channel.name.startswith("ticket-"):
        await ctx.send("This is not a ticket channel.")
        return

    await channel.set_permissions(user, view_channel=True, send_messages=True, attach_files=True)
    await ctx.send(f"{user.mention} has been added to the ticket.")

@bot.command()
@commands.has_permissions(manage_channels=True)
async def removeuser(ctx, user: discord.Member):
    """Removes a user from the ticket channel."""
    channel = ctx.channel
    if not channel.name.startswith("ticket-"):
        await ctx.send("This is not a ticket channel.")
        return

    await channel.set_permissions(user, view_channel=False)
    await ctx.send(f"{user.mention} has been removed from the ticket.")

# Error handling
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("You do not have permission to use this command.")
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("Please provide all required arguments.")
    elif isinstance(error, commands.BadArgument):
        await ctx.send("Invalid argument provided.")
    else:
        print(f"Error: {error}")
        await ctx.send(f"An error occurred: {error}")
keep_alive()
# Run the bot
load_dotenv()  # Load environment variables from .env file


bot.run(os.getenv("TOKEN"))  # Use the token from the .env file  
