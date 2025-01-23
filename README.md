<div align="center">
  <h2 align="center">GitHub Repository Bot</h2>
  <p align="center">
    A Discord bot that automatically announces new GitHub repositories and their updates in real-time.
    <br />
    <br />
    <a href="https://discord.cyberious.xyz">💬 Discord</a>
    ·
    <a href="#-changelog">📜 ChangeLog</a>
    ·
    <a href="https://github.com/sexfrance/Github-Repository-Bot/issues">⚠️ Report Bug</a>
    ·
    <a href="https://github.com/sexfrance/Github-Repository-Bot/issues">💡 Request Feature</a>
  </p>
</div>

---

### ⚙️ Installation

- Requires: `Python 3.7+`
- Make a python virtual environment: `python3 -m venv venv`
- Source the environment: `venv\Scripts\activate` (Windows) / `source venv/bin/activate` (macOS, Linux)
- Install the requirements: `pip install -r requirements.txt`

---

### 🔥 Features

- Real-time GitHub repository monitoring
- Beautiful embed messages with repository details
- Repository stats tracking (Stars, Forks, Watchers)
- Support for multiple bot owners
- Customizable embed appearance
- Repository preview images
- Detailed repository information
- Hex color support for embeds
- Owner-only command system

---

### 📝 Usage

1. **Configuration**:
   Edit `config.toml`:

   ```toml
   [BOT]
   Token = "your-discord-bot-token"
   Owner = [your-discord-id]  # Can add multiple owner IDs

   [SERVER]
   Channel = channel-id-for-announcements
   GitHub_Username = "your-github-username"

   [Embed]
   title = "New Repository Created!"
   color = "#3498db"
   thumbnail = "path-to-thumbnail"
   footer_text = "Custom footer text"
   show_timestamp = true
   ```

2. **Bot Commands**:

   - `.set_channel <channel_id>` - Set announcement channel
   - `.set_username <github_username>` - Set GitHub username to monitor
   - `.set_embed <setting> <value>` - Customize embed appearance
   - `.show_embed_settings` - View current embed settings
   - `.add_owner <user_id>` - Add a bot owner
   - `.remove_owner <user_id>` - Remove a bot owner
   - `.list_owners` - Show all bot owners

3. **Running the bot**:
   ```bash
   python main.py
   ```

---

### 📹 Embed Preview

![Sex](https://i.imgur.com/MubOyuL.png)

---

### ❗ Disclaimers

- This project is for educational purposes only
- Use responsibly and in accordance with Discord's terms of service
- Respect GitHub's API rate limits

---

### 📜 ChangeLog

```diff
v1.0.0 ⋮ 12/26/2024
! Initial release

```

<p align="center">
  <img src="https://img.shields.io/github/license/sexfrance/Github-Repository-Bot.svg?style=for-the-badge&labelColor=black&color=f429ff&logo=IOTA"/>
  <img src="https://img.shields.io/github/stars/sexfrance/Github-Repository-Bot.svg?style=for-the-badge&labelColor=black&color=f429ff&logo=IOTA"/>
  <img src="https://img.shields.io/github/languages/top/sexfrance/Github-Repository-Bot.svg?style=for-the-badge&labelColor=black&color=f429ff&logo=python"/>
</p>
