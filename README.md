1. 🧾 **Header**
# 🤖 Telegram Media Cloner Bot 🚀

*********Working Only in Public Channel or group********

A powerful Telegram bot that clones media (images, videos, GIFs) from public channels to your group with queue management and caption support.

![Python](https://img.shields.io/badge/Python-3.10+-blue?logo=python)
![Platform](https://img.shields.io/badge/Platform-Telegram-blue?logo=telegram)
![Author](https://img.shields.io/badge/Author-AvroHere-green?logo=github)

2. 🧩 **Features**
- **📥 Batch Processing**: Process multiple links from text files or direct messages
- **⏯️ Queue Control**: Pause/resume processing with `/stopnow` and `/startnow`
- **📝 Smart Captions**: Add captions to multiple media files with `/cap` command
- **⏭️ Skip Feature**: Jump ahead in queue with `/skip N` command
- **📊 Progress Tracking**: See current position and total links with `/list`
- **⏳ Rate Limited**: Built-in delays to avoid Telegram API limits
- **🛡️ Admin Protected**: Only authorized users can control the bot
- **📄 Export Queue**: Save remaining links as a text file with `/remain`

3. 💾 **Installation
```bash
# Clone the repository
git clone https://github.com/AvroHere/telegram-media-cloner.git
cd telegram-media-cloner

# Install dependencies
pip install -r requirements.txt

# Configure the bot
# Edit main.py with your API credentials and target group ID

# Run the bot
python main.py
```


```markdown
4. 🔥 **Usage**

**Usage Methods:**
1. **Single Link**: `/clone https://t.me/channel/123`
2. **Text File**: Upload a `.txt` file with multiple links
3. **Queue Management**: Use commands to control processing

**Numbered Instructions:**
1. 🏸 `/stopnow` - Pause processing  
2. ▶️ `/startnow` - Resume processing  
3. 📋 `/list` - Show current queue  
4. 🧹 `/clean` - Clear all queued links  
5. ⏭️ `/skip 5` - Skip next 5 links  
6. 📝 `/cap 3 My Caption` - Add caption to next 3 media  
7. 🛑 `/capstop` - Stop adding captions  
8. 📄 `/remain` - Export remaining links  
9. ℹ️ `/help` - Show all commands
```

**Remember**

🐍 Install Python 3.10+ if not already installed

🔑 Get API credentials from my.telegram.org

🤖 Create a bot via @BotFather

🏸 Use /stopnow to pause processing anytime

▶️ Resume with /startnow when ready

📤 Send .txt files or direct links to start cloning


5. 📁 **Folder Structure**

```telegram-media-cloner/
├── main.py            # Main bot script
├── README.md          # This documentation
├── requirements.txt   # Dependency list
└── LICENSE.txt        # MIT License file
```

6. 🛠 **Built With**
- External Libraries:
  - `telethon >= 1.28.5` - Telegram API client
- Standard Libraries:
  - `asyncio` - For asynchronous operations
  - `re` - Regular expressions for link parsing
  - `os` - File system operations
  - `time` - For delays between operations
 
  7. 🚧 **Roadmap**
- [ ] Add support for YouTube links
- [ ] Implement automatic watermarking
- [ ] Add database persistence for queue
- [ ] Create web dashboard for monitoring
- [ ] Support multiple target groups
- [ ] Add media type filtering (only videos/images)

8. ❓ **FAQ**
**Q: Why are some messages not being cloned?**  
A: The bot only clones media messages (images, videos, GIFs). Text messages are automatically skipped.

**Q: How to change the target group?**  
A: Modify the `TARGET_GROUP_ID` variable in the script with your new group's ID (including the -100 prefix).

9. 📄 **License**
MIT License

Copyright (c) 2025 AvroHere

Permission is hereby granted... [full license text in LICENSE.txt]

10. 👨‍💻 **Author**
**Avro**  
GitHub: [https://github.com/AvroHere](https://github.com/AvroHere)  

*"Code is like humor. When you have to explain it, it's bad."* - Cory House  

⭐ If you find this project useful, please star it on GitHub!

