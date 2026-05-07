# 💎 Mr.White - Instagram DM Backup & Analytics Tool

> *"I am the one who backs up."* 🧪

![Python](https://img.shields.io/badge/Python-3.7+-blue.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)
![Status](https://img.shields.io/badge/Status-Active-brightgreen.svg)

A powerful Instagram DM backup and analytics tool that securely archives your direct messages with advanced features like media download, conversation analytics, and intelligent search.

---

## ✨ Features

### 🔐 Core Functionality
- **Session-Based Authentication** - Secure login using Instagram session IDs
- **Full Conversation Backup** - Download complete message history with all metadata
- **Media Download** - Automatically capture images, videos, voice messages, and reels
- **Multiple Export Formats** - Save as TXT, JSON, and interactive HTML

### 📊 Analytics Dashboard
- **Message Statistics** - Total messages, conversations, unique senders
- **Peak Activity Analysis** - Identify busiest hours and days
- **Word Frequency** - Top words used across conversations
- **Message Type Distribution** - Breakdown of text, media, voice, reels, etc.
- **Conversation Rankings** - Most active conversations
- **User Rankings** - Most active participants
- **Visual Charts** - Beautiful graphical representations

### 🔍 Search & Organization
- **Full-Text Search** - Find messages across all backed-up conversations
- **Content Filtering** - Search by text, URLs, or media type
- **Quick Results** - Instant search across thousands of messages

### 📦 Archive & Export
- **ZIP Compression** - Create compressed backups of all data
- **Organized Structure** - Conversations sorted in dedicated folders
- **Media Preservation** - All media files preserved with original quality

### 🎨 Beautiful UI
- **Interactive HTML Viewer** - View conversations with beautiful dark/light theme
- **Responsive Design** - Works on desktop and mobile
- **Search in Viewer** - Find messages within conversation HTML
- **Professional Dashboard** - Stunning analytics visualization

---

## 🚀 Quick Start

### Prerequisites
```bash
python 3.7+
pip (Python package manager)
```

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/zerosocialcode/MrWhite.git
cd MrWhite
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Get Your Instagram Session ID**
   - Open Instagram in your browser (web.instagram.com)
   - Open Developer Tools (F12)
   - Go to Application → Cookies → web.instagram.com
   - Find the cookie named `sessionid`
   - Copy its value

4. **Add Your Session ID**
   - Open `mainvlast.py`
   - Find line with `SESSION_ID = "your instagram sessionid"`
   - Replace with your actual session ID
   - ⚠️ Keep it private! Never share this value

5. **Run the tool**
```bash
python mainvlast.py
```

---

## 📖 Usage Guide

### Main Menu Options

```
💎 MR.WHITE MAIN MENU
==================================================
  1. 📥 Download conversations
  2. 📊 Generate analytics dashboard
  3. 🔍 Search through backups
  4. 📦 Create ZIP archive
  5. 🚪 Exit
```

### Option 1: Download Conversations

1. Select option `1` from main menu
2. Choose conversations to download:
   - Enter conversation numbers: `1,2,3`
   - Or ranges: `1-5`
   - Or select all: `all`
3. Tool automatically:
   - Downloads all messages
   - Captures media files
   - Extracts reel links
   - Processes reactions and replies

**Output Files:**
```
mrwhite_backups/
├── Conversation_Name/
│   ├── Conversation_Name.txt          # Plain text format
│   ├── Conversation_Name.json         # Structured data
│   ├── Conversation_Name.html         # Interactive viewer
│   ├── Conversation_Name_reels.txt    # Shared reels links
│   └── media/                         # Downloaded media files
```

### Option 2: Analytics Dashboard

1. Download at least one conversation (Step 1)
2. Select option `2` from main menu
3. Dashboard is generated at: `mrwhite_backups/analytics/dashboard.html`

**Dashboard Includes:**
- 📊 Total message count
- 💬 Conversation breakdown
- 👤 Most active participants
- ⏰ Peak activity hours
- 📅 Messages by day of week
- 🔤 Top words analysis
- 📈 Message type distribution
- 📋 User rankings

### Option 3: Search Backups

1. Select option `3` from main menu
2. Enter your search query (any text, URL, or partial phrase)
3. View all matching messages with context

### Option 4: Create Archive

1. Select option `4` from main menu
2. Creates timestamped ZIP file with all backups
3. Example: `mrwhite_backup_20240515_143022.zip`

---

## 📁 Output Structure

```
mrwhite_backups/
├── Analytics/
│   ├── dashboard.html              # Main analytics dashboard
│   └── stats.json                  # Raw statistics (JSON)
│
├── Conversation_1/
│   ├── Conversation_1.txt          # Text export
│   ├── Conversation_1.json         # JSON export
│   ├── Conversation_1.html         # Interactive HTML viewer
│   ├── Conversation_1_reels.txt    # Extracted reel links
│   └── media/
│       ├── message_id_timestamp.jpg
│       ├── message_id_timestamp.mp4
│       └── ...
│
└── Conversation_2/
    └── (same structure as above)
```

---

## 🎯 Supported Message Types

Mr.White automatically detects and processes:

| Type | Icon | Export |
|------|------|--------|
| Text Messages | 💬 | ✅ Full text |
| Photos | 📷 | ✅ Download + Link |
| Videos | 🎬 | ✅ Download + Link |
| Reels | 📽️ | ✅ Instagram link |
| Voice Messages | 🎤 | ✅ Download |
| Links | 🔗 | ✅ URL preserved |
| Reactions | ❤️ | ✅ Emoji list |
| Replies | ↳ | ✅ Thread context |
| Stories | 📖 | ✅ Marked |
| Clips | 🎬 | ✅ Links |

---

## 🔒 Security & Privacy

**Important:**
- Session IDs are stored locally in the script - keep them private
- Never commit session IDs to version control
- Use `.gitignore` to exclude session data
- Media files are downloaded locally - not uploaded anywhere
- This tool is for personal backup only
- Respect Instagram's Terms of Service and users' privacy

**Best Practices:**
```bash
# Add to .gitignore
mainvlast.py  # Don't commit files with session IDs
*.json        # Don't commit backup data
mrwhite_backups/
*.zip
```

---

## ⚙️ Configuration

### Session Management
Edit the session ID in `mainvlast.py`:
```python
SESSION_ID = "your_actual_instagram_session_id_here"
```

### Backup Directory
Change default location:
```python
mr_white = MrWhite(backup_dir="custom_backup_path")
```

### Download Limits
The tool fetches:
- All available messages in a conversation
- All available media files (subject to bandwidth)
- Up to recent message history

---

## 🐛 Troubleshooting

### Login Failed
```
❌ Cook failed: Error message
```
**Solution:**
- Verify session ID is correct
- Check if session has expired
- Try getting a new session ID
- Ensure Instagram account is accessible

### No Conversations Found
```
❌ No conversations found!
```
**Solution:**
- Ensure account is logged in properly
- Wait a few seconds and try again
- Check internet connection
- Verify DM inbox is not empty

### Media Download Fails
**Solution:**
- Check internet connection
- Increase timeout value in code
- Some media may require authentication
- Instagram may be blocking downloads

### HTML Viewer Not Working
**Solution:**
- Open HTML file in modern browser (Chrome, Firefox, Safari, Edge)
- Check browser console for errors (F12)
- Ensure media files are in correct path

---

## 📊 Analytics Explained

### Peak Hours
Shows which hours of the day have most message activity. Useful for understanding communication patterns.

### Messages by Day
Breakdown by weekday. Helps identify if certain days are busier.

### Top Words
Frequency analysis of words used in text messages (excluding common words). Shows conversation themes.

### Message Types
Distribution of different message types (text vs media vs voice, etc.).

### Top Conversations
Which conversations have the most messages.

### Most Active People
Users who sent the most messages across all conversations.

---

## 🛠️ Dependencies

```
instagrapi>=2.0.0      # Instagram API client
requests>=2.28.0       # HTTP library for media downloads
```

Install all dependencies:
```bash
pip install -r requirements.txt
```

---

## 📝 File Formats

### .txt Format
Human-readable plaintext export with formatting:
```
[1] 15 May 2024, 10:30 AM | @username
↳ Previous message preview
This is the message text
📽️ https://www.instagram.com/reel/...
📎 media/12345_1234567890.jpg
Reactions: ❤️ 😂 👍
----------------------------------------
```

### .json Format
Structured data for programmatic access:
```json
{
  "conversation": "Chat Name",
  "thread_id": "123456789",
  "participants": ["user1", "user2"],
  "message_count": 1500,
  "messages": [
    {
      "id": "msg_123",
      "timestamp": "2024-05-15T10:30:00",
      "sender_username": "username",
      "type": "text",
      "text": "Hello!",
      "reactions": []
    }
  ]
}
```

### .html Format
Interactive viewer with:
- Dark/Light theme toggle
- Search functionality
- Embedded media
- Reply threads
- Reaction emojis
- Mobile responsive

---

## 🎨 HTML Viewer Features

- **Theme Toggle** 🌓 - Switch between dark and light mode
- **Search** 🔍 - Find messages in real-time
- **Statistics** 📊 - Message type breakdown
- **Media Preview** 📷 - Inline images and videos
- **Responsive** 📱 - Works on all devices
- **Performance** ⚡ - Lazy loading for images
- **Professional Design** ✨ - Beautiful dark theme

---

## 📈 Performance

- **Download Speed**: Depends on message count and media size
  - ~100 messages: ~10 seconds
  - ~1000 messages: ~2-5 minutes
  - ~10000 messages: ~30-60 minutes

- **Storage**: Varies by media
  - Text only: ~100 KB per 1000 messages
  - With media: 500 MB - 5 GB+ per conversation

- **Search**: Instant for <50k messages

---

## 🤝 Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create feature branch: `git checkout -b feature/AmazingFeature`
3. Commit changes: `git commit -m 'Add AmazingFeature'`
4. Push to branch: `git push origin feature/AmazingFeature`
5. Open a Pull Request

---

## ⚠️ Disclaimer

**This tool is provided for educational and personal backup purposes only.**

- Respect Instagram's Terms of Service
- Only backup your own conversations
- Respect privacy of others in conversations
- Use responsibly and legally
- The author is not responsible for misuse

**Instagram Session ID Security:**
- Keep your session ID completely private
- Never share it with anyone
- Treat it like a password
- Regenerate if compromised
- Use a dedicated account for backups if possible

---

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

## 👨‍💼 Author

**Developed by anharhussan**

> *"I am the one who backs up."* 🧪

---

## 🎬 Breaking Bad Reference

This tool is inspired by Walter White's meticulous nature and attention to detail. Just as Mr. White carefully documented his "empire," Mr.White tool helps you meticulously backup your digital conversations.

---

## 📞 Support

For issues, bugs, or feature requests:
- Open an GitHub Issue
- Check existing issues for similar problems
- Provide detailed error messages and screenshots

---

## 🔄 Version History

**v3.0** - Current Version
- Full analytics dashboard
- Enhanced media handling
- Improved search functionality
- Better error handling
- Beautiful UI with dark mode

---

## 🚀 Roadmap

- [ ] Two-factor authentication support
- [ ] Scheduled automatic backups
- [ ] Cloud storage integration
- [ ] Advanced filtering options
- [ ] Conversation export to various formats
- [ ] Multi-account support

---

## ⭐ Star this repository if you find it useful!

```
╔══════════════════════════════════════════════════════════╗
║                                                          ║
║   ███╗   ███╗██████╗     ██╗    ██╗██╗  ██╗██╗████████╗███████╗
║   ████╗ ████║██╔══██╗    ██║    ██║██║  ██║██║╚══██╔══╝██╔════╝
║   ██╔████╔██║██████╔╝    ██║ █╗ ██║███████║██║   ██║   █████╗  
║   ██║╚██╔╝██║██╔══██╗    ██║███╗██║██╔══██║██║   ██║   ██╔══╝  
║   ██║ ╚═╝ ██║██║  ██║    ╚███╔███╔╝██║  ██║██║   ██║   ███████╗
║   ╚═╝     ╚═╝╚═╝  ╚═╝     ╚══╝╚══╝ ╚═╝  ╚═╝╚═╝   ╚═╝   ╚══════╝
║                                                          ║
║           Instagram DM Backup & Analytics Tool v3.0      ║
║           Developed by anharhussan                        ║
║           "I am the one who backs up."                   ║
╚══════════════════════════════════════════════════════════╝
```

---

**Last Updated:** May 7, 2026
