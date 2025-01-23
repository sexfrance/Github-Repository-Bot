import discord
import aiohttp
import asyncio
import toml
import re
import datetime
from discord.ext import commands
from datetime import UTC  # Add this import

CONFIG_FILE = "config.toml"

class RepoState:
    def __init__(self, repo):
        self.id = repo['id']
        self.stars = repo['stargazers_count']
        self.forks = repo['forks_count']
        self.watchers = repo['watchers_count']
        self.description = repo.get('description', '')
        self.last_update = repo['updated_at']
        self.name = repo['name']

    def __str__(self):
        return f"Repo {self.name}: {self.stars}⭐ {self.forks}🍴 {self.watchers}👀"

repo_states = {}

def load_config():
    try:
        with open(CONFIG_FILE, "r") as f:
            return toml.load(f)
    except FileNotFoundError:
        return {
            "BOT": {"Token": "", "Owner": []},
            "Server": {
                "Channel": 0,
                "GitHub_Username": "",
            },
            "Embed": {
                "title": "New Repository Created!",
                "color": "0x3498db",
                "thumbnail": "https://github.githubassets.com/images/modules/logos_page/GitHub-Mark.png",
                "footer_text": "GitHub Repository Bot",
                "show_timestamp": True
            }
        }

def save_config(config):
    with open(CONFIG_FILE, "w") as f:
        toml.dump(config, f)

def hex_to_int(hex_str: str) -> int:
    hex_str = hex_str.replace('#', '').replace('0x', '')
    return int(hex_str, 16)

config = load_config()
DISCORD_TOKEN = config["BOT"].get("Token", "")
CHANNEL_ID = config["SERVER"].get("Channel", 0)
GITHUB_USERNAME = config["SERVER"].get("GitHub_Username", "")

bot = commands.Bot(command_prefix=".", intents=discord.Intents.all())

async def fetch_repos():
    url = f"https://api.github.com/users/{GITHUB_USERNAME}/repos"
    headers = {
        "Accept": "application/vnd.github.v3+json",
        "User-Agent": "GitHub-Repository-Bot"
    }
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as response:
            if response.status == 200:
                return await response.json()
            return None

def has_repo_changed(repo, old_state):
    """Compare old and new state of repository, return True if changed"""
    changes = []
    
    if repo['stargazers_count'] != old_state.stars:
        changes.append(f"Stars changed: {old_state.stars} -> {repo['stargazers_count']}")
    if repo['forks_count'] != old_state.forks:
        changes.append(f"Forks changed: {old_state.forks} -> {repo['forks_count']}")
    if repo['watchers_count'] != old_state.watchers:
        changes.append(f"Watchers changed: {old_state.watchers} -> {repo['watchers_count']}")
    if repo.get('description', '') != old_state.description:
        changes.append("Description changed")
    
    if changes:
        return True
    return False

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")
    channel = bot.get_channel(CHANNEL_ID)
    
    current_time = datetime.datetime.now(UTC)

    initial_repos = await fetch_repos()
    if initial_repos:
        for repo in initial_repos:
            repo_states[repo['id']] = RepoState(repo)
    
    while True:
        if GITHUB_USERNAME:
            try:
                repos = await fetch_repos()
                if repos:
                    for repo in repos:
                        repo_id = repo['id']
                        repo_created = datetime.datetime.strptime(
                            repo['created_at'], 
                            "%Y-%m-%dT%H:%M:%SZ"
                        ).replace(tzinfo=UTC)
                        
                        if repo_created > current_time:
                            description = (
                                f"**{repo['name']}**\n"
                                f"{repo.get('description', 'No description provided.')}\n"
                                f"\n━━━━━━━━━━━━━━━\n"
                                f"📊 **Stats**\n"
                                f"⭐ Stars: `{repo['stargazers_count']}`\n"
                                f"🍴 Forks: `{repo['forks_count']}`\n"
                                f"👀 Watchers: `{repo['watchers_count']}`\n"
                                f"\n━━━━━━━━━━━━━━━\n"
                                f"🔗 **Quick Links**\n"
                                f"• [View Repository]({repo['html_url']})\n"
                                f"• [Download ZIP]({repo['html_url']}/archive/refs/heads/main.zip)"
                            )

                            embed = discord.Embed(
                                title=config["Embed"].get("title", "🎉 New Repository Created!"),
                                description=description,
                                url=repo["html_url"],
                                color=hex_to_int(config["Embed"].get("color", "#3498db"))
                            )
                            
                            timestamp = int(datetime.datetime.now(UTC).timestamp())
                            preview_url = f"https://opengraph.githubassets.com/{timestamp}/{GITHUB_USERNAME}/{repo['name']}"
                            embed.set_image(url=preview_url)
                            
                            if config["Embed"].get("thumbnail"):
                                embed.set_thumbnail(url=config["Embed"]["thumbnail"])
                            
                            embed.add_field(
                                name="📝 Language", 
                                value=f"`{repo.get('language', 'Not specified')}`", 
                                inline=True
                            )
                            
                            license_info = repo.get("license")
                            license_name = "No license"
                            if isinstance(license_info, dict):
                                license_name = license_info.get("name", "No license")
                            embed.add_field(
                                name="📜 License", 
                                value=f"`{license_name}`", 
                                inline=True
                            )
                            
                            embed.add_field(
                                name="🔒 Visibility",
                                value=f"`{repo.get('visibility', 'Unknown').capitalize()}`",
                                inline=True
                            )
                            
                            created_at = datetime.datetime.strptime(repo["created_at"], "%Y-%m-%dT%H:%M:%SZ")
                            embed.add_field(
                                name="📅 Created",
                                value=f"`{created_at.strftime('%Y-%m-%d %H:%M')} UTC`",
                                inline=True
                            )
                            
                            footer_text = config["Embed"].get("footer_text", "GitHub Repository Bot")
                            embed.set_footer(
                                text=f"{footer_text} • {GITHUB_USERNAME}",
                                icon_url=config["Embed"].get("thumbnail")
                            )
                            
                            if config["Embed"].get("show_timestamp", True):
                                embed.timestamp = datetime.datetime.now(UTC)

                            if channel:
                                await channel.send(embed=embed)
                                repo_states[repo_id] = RepoState(repo)
                        
                        elif repo_id in repo_states and has_repo_changed(repo, repo_states[repo_id]):
                            description = (
                                f"**{repo['name']}**\n"
                                f"{repo.get('description', 'No description provided.')}\n"
                                f"\n━━━━━━━━━━━━━━━\n"
                                f"📊 **Stats**\n"
                                f"⭐ Stars: `{repo['stargazers_count']}`\n"
                                f"🍴 Forks: `{repo['forks_count']}`\n"
                                f"👀 Watchers: `{repo['watchers_count']}`\n"
                                f"\n━━━━━━━━━━━━━━━\n"
                                f"🔗 **Quick Links**\n"
                                f"• [View Repository]({repo['html_url']})\n"
                                f"• [Download ZIP]({repo['html_url']}/archive/refs/heads/main.zip)"
                            )

                            embed = discord.Embed(
                                title=config["Embed"].get("title", "🎉 New Repository Created!"),
                                description=description,
                                url=repo["html_url"],
                                color=hex_to_int(config["Embed"].get("color", "#3498db"))
                            )
                            
                            timestamp = int(datetime.datetime.now(UTC).timestamp())
                            preview_url = f"https://opengraph.githubassets.com/{timestamp}/{GITHUB_USERNAME}/{repo['name']}"
                            embed.set_image(url=preview_url)
                            
                            if config["Embed"].get("thumbnail"):
                                embed.set_thumbnail(url=config["Embed"]["thumbnail"])
                            
                            embed.add_field(
                                name="📝 Language", 
                                value=f"`{repo.get('language', 'Not specified')}`", 
                                inline=True
                            )
                            
                            license_info = repo.get("license")
                            license_name = "No license"
                            if isinstance(license_info, dict):
                                license_name = license_info.get("name", "No license")
                            embed.add_field(
                                name="📜 License", 
                                value=f"`{license_name}`", 
                                inline=True
                            )
                            
                            embed.add_field(
                                name="🔒 Visibility",
                                value=f"`{repo.get('visibility', 'Unknown').capitalize()}`",
                                inline=True
                            )
                            
                            created_at = datetime.datetime.strptime(repo["created_at"], "%Y-%m-%dT%H:%M:%SZ")
                            embed.add_field(
                                name="📅 Created",
                                value=f"`{created_at.strftime('%Y-%m-%d %H:%M')} UTC`",
                                inline=True
                            )
                            
                            footer_text = config["Embed"].get("footer_text", "GitHub Repository Bot")
                            embed.set_footer(
                                text=f"{footer_text} • {GITHUB_USERNAME}",
                                icon_url=config["Embed"].get("thumbnail")
                            )
                            
                            if config["Embed"].get("show_timestamp", True):
                                embed.timestamp = datetime.datetime.now(UTC)

                            if channel:
                                await channel.send(embed=embed)
                            repo_states[repo_id] = RepoState(repo)
                    
            except Exception as e:
                print(f"Error during repository check: {e}")
            
        await asyncio.sleep(60)

def is_owner():
    async def predicate(ctx):
        return ctx.author.id in config["BOT"].get("Owner", [])
    return commands.check(predicate)

@bot.command()
@is_owner()
async def add_owner(ctx, user_id: int):
    if "owners" not in config["Server"]:
        config["Server"]["owners"] = []
    if user_id not in config["Server"]["owners"]:
        config["Server"]["owners"].append(user_id)
        save_config(config)
        await ctx.send(f"Added user {user_id} to owners list.")
    else:
        await ctx.send("This user is already an owner.")

@bot.command()
@is_owner()
async def remove_owner(ctx, user_id: int):
    if user_id in config["Server"].get("owners", []):
        config["Server"]["owners"].remove(user_id)
        save_config(config)
        await ctx.send(f"Removed user {user_id} from owners list.")
    else:
        await ctx.send("This user is not an owner.")

@bot.command()
@is_owner()
async def list_owners(ctx):
    owners = config["Server"].get("owners", [])
    if owners:
        owner_list = "\n".join([f"• {owner_id}" for owner_id in owners])
        await ctx.send(f"**Bot Owners:**\n{owner_list}")
    else:
        await ctx.send("No owners configured.")

@bot.command()
@is_owner()
async def set_channel(ctx, channel_id: int):
    global CHANNEL_ID
    CHANNEL_ID = channel_id
    config["channel_id"] = channel_id
    save_config(config)
    await ctx.send(f"Channel ID set to {channel_id}.")

@bot.command()
@is_owner()
async def set_username(ctx, username: str):
    global GITHUB_USERNAME
    GITHUB_USERNAME = username
    config["github_username"] = username
    save_config(config)
    await ctx.send(f"GitHub username set to {username}.")

@bot.command()
@is_owner()
async def set_token(ctx, token: str):
    global DISCORD_TOKEN
    DISCORD_TOKEN = token
    config["discord_token"] = token
    save_config(config)
    await ctx.send("Discord token updated.")

@bot.command()
@is_owner()
async def set_embed(ctx, setting: str, *, value: str):
    setting = setting.lower()
    valid_settings = ["title", "color", "thumbnail", "footer_text", "show_timestamp"]
    
    if setting not in valid_settings:
        await ctx.send(f"Invalid setting. Valid options are: {', '.join(valid_settings)}")
        return
    
    if setting == "color":
        hex_pattern = re.compile(r'^#?(?:[0-9a-fA-F]{3}){1,2}$|^0x[0-9a-fA-F]{6}$')
        if not hex_pattern.match(value.replace('0x', '#')):
            await ctx.send("Invalid color format. Use hex format (e.g., #3498db, #fff, 0x3498db)")
            return
    
    if setting == "show_timestamp":
        value = value.lower() == "true"
    
    if "Embed" not in config:
        config["Embed"] = {}
    
    config["Embed"][setting] = value
    save_config(config)
    await ctx.send(f"Embed {setting} updated to: {value}")

@bot.command()
@is_owner()
async def show_embed_settings(ctx):

    embed = discord.Embed(
        title="Current Embed Settings", 
        color=hex_to_int(config["Embed"].get("color", "#3498db"))
    )
    for setting, value in config.get("Embed", {}).items():
        embed.add_field(name=setting, value=str(value), inline=False)
    await ctx.send(embed=embed)

bot.run(DISCORD_TOKEN)
