# mrwhite.py
# Mr.White - Instagram DM Backup & Analytics Tool
# Developed by anharhussan
# "I am the one who backs up."

import os
import json
import time
import base64
import re
import zipfile
import shutil
from datetime import datetime, timedelta
from collections import Counter, defaultdict
from instagrapi import Client
import requests
from pathlib import Path
from urllib.parse import unquote
import logging

# Suppress warnings
logging.basicConfig(level=logging.CRITICAL)
logging.getLogger('instagrapi').setLevel(logging.CRITICAL)
logging.getLogger('urllib3').setLevel(logging.CRITICAL)
logging.getLogger('requests').setLevel(logging.CRITICAL)

BANNER = r"""
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
"""

class MrWhite:
    def __init__(self, backup_dir="mrwhite_backups"):
        self.client = Client()
        self.backup_dir = Path(backup_dir)
        self.backup_dir.mkdir(exist_ok=True)
        self.username_cache = {}
        self.all_messages = {}
        
    def login(self):
        """Login using session ID"""
        SESSION_ID = "your instagram sessionid"
        
        try:
            self.client.set_user_agent("Instagram 269.0.0.18.75 Android")
            self.client.login_by_sessionid(SESSION_ID)
            user_info = self.client.account_info()
            print(f"✅ Authenticated as: @{user_info.username}")
            return True, user_info.username
        except Exception as e:
            print(f"❌ Cook failed: {e}")
            return False, None
    
    def get_username_safe(self, user_id):
        if user_id in self.username_cache:
            return self.username_cache[user_id]
        try:
            username = self.client.username_from_user_id(user_id)
            self.username_cache[user_id] = username
            return username
        except:
            username = str(user_id)
            self.username_cache[user_id] = username
            return username
    
    def extract_media_id_from_cache_key(self, cache_key):
        try:
            decoded = base64.b64decode(cache_key).decode('utf-8')
            return decoded.split('_')[0]
        except:
            return None
    
    def extract_reel_url_from_preview(self, preview_url):
        if not preview_url:
            return None
        if 'ig_cache_key=' in preview_url:
            try:
                start = preview_url.index('ig_cache_key=') + 13
                end = preview_url.index('&', start) if '&' in preview_url[start:] else len(preview_url)
                cache_key = unquote(preview_url[start:end])
                if '.2-' in cache_key:
                    cache_key = cache_key.split('.2-')[0]
                media_id = self.extract_media_id_from_cache_key(cache_key)
                if media_id:
                    try:
                        media_info = self.client.media_info(media_id)
                        if media_info and hasattr(media_info, 'code') and media_info.code:
                            return f"https://www.instagram.com/p/{media_info.code}/"
                    except:
                        pass
            except:
                pass
        return None
    
    def download_media(self, url, conversation_name, message_id, media_type="media"):
        if not url:
            return None
        media_dir = self.backup_dir / conversation_name / "media"
        media_dir.mkdir(parents=True, exist_ok=True)
        try:
            ext = 'mp4' if any(x in url.lower() for x in ['mp4', 'video']) else 'mp3' if any(x in url.lower() for x in ['mp3', 'audio']) else 'jpg'
            filename = f"{message_id}_{int(time.time())}.{ext}"
            filepath = media_dir / filename
            response = requests.get(url, timeout=60)
            if response.status_code == 200 and len(response.content) > 0:
                with open(filepath, 'wb') as f:
                    f.write(response.content)
                return f"media/{filename}"
        except:
            pass
        return None
    
    def list_conversations(self):
        print("\n📥 Fetching conversations...")
        try:
            threads = self.client.direct_threads(amount=0)
            if not threads:
                print("❌ No conversations found!")
                return []
            print(f"\nFound {len(threads)} conversations:\n")
            print("=" * 70)
            for idx, thread in enumerate(threads, 1):
                title = thread.thread_title if thread.thread_title else "Unnamed Chat"
                participants = []
                if hasattr(thread, 'users') and thread.users:
                    for user_id in thread.users:
                        username = self.get_username_safe(user_id)
                        if not username.startswith("pk=") and username not in participants:
                            participants.append(username)
                names = ", ".join(participants[:3]) + (f" +{len(participants)-3} more" if len(participants) > 3 else "")
                if not participants:
                    names = title
                preview = ""
                if hasattr(thread, 'messages') and thread.messages:
                    try:
                        last_msg = thread.messages[0]
                        type_map = {"text": last_msg.text[:60] if last_msg.text else "", "media_share": "📷 Photo/Video", "voice_media": "🎤 Voice", "like": "❤️ Like", "clip": "📽️ Clip", "xma_clip": "📽️ Reel", "reel_share": "📽️ Reel", "link": "🔗 Link", "xma_profile": "👤 Profile", "generic_xma": "📎 Content"}
                        preview = type_map.get(last_msg.item_type, f"[{last_msg.item_type}]")
                        if isinstance(preview, str) and len(preview) > 60:
                            preview = preview[:60] + "..."
                    except:
                        preview = ""
                print(f"[{idx}] {title}")
                if names != title:
                    print(f"    Chat: {names}")
                if preview:
                    print(f"    Last: {preview}")
                print()
                time.sleep(0.2)
            print("=" * 70)
            print("\n📋 Select: numbers (1,2,3 or 1-3), 'all', or '0' to cancel")
            while True:
                choice = input("\n🎯 Which to download? ").strip()
                if choice.lower() == 'all':
                    return threads
                elif choice == '0':
                    return []
                selected = set()
                try:
                    for part in choice.split(','):
                        part = part.strip()
                        if '-' in part:
                            start, end = map(int, part.split('-'))
                            selected.update(range(start, end + 1))
                        else:
                            selected.add(int(part))
                    valid = sorted([i for i in selected if 1 <= i <= len(threads)])
                    if not valid:
                        print("⚠ Invalid!")
                        continue
                    selected_threads = [threads[i-1] for i in valid]
                    print(f"\n✅ Selected {len(selected_threads)}:")
                    for t in selected_threads:
                        print(f"  • {t.thread_title}")
                    if input("\n🚀 Start? (y/n): ").strip().lower() == 'y':
                        return selected_threads
                except ValueError:
                    print("⚠ Use numbers like: 1,2,5 or 1-3")
        except Exception as e:
            print(f"❌ Error: {e}")
            return []
    
    def process_conversation(self, thread):
        title = thread.thread_title if thread.thread_title else "Unnamed"
        conv_name = self._sanitize(title)
        print(f"\n{'='*60}")
        print(f"📱 {title}")
        print(f"{'='*60}")
        try:
            conv_dir = self.backup_dir / conv_name
            conv_dir.mkdir(parents=True, exist_ok=True)
            print("📨 Fetching...")
            messages = self.client.direct_messages(thread.id, amount=0)
            total = len(messages)
            if total == 0:
                print("  ⚠ Empty!")
                return False
            print(f"  {total} messages")
            print("🔄 Processing...")
            formatted = []
            reel_urls = []
            for i, msg in enumerate(reversed(messages), 1):
                if i % 200 == 0:
                    print(f"  {i}/{total}...")
                data = self._process_message(msg, conv_name)
                if data:
                    formatted.append(data)
                    if data.get('reel_url'):
                        reel_urls.append({'timestamp': data['timestamp'], 'sender': data['sender_username'], 'url': data['reel_url'], 'text': data.get('text', '')})
                time.sleep(0.15)
            
            # Store for analytics
            self.all_messages[conv_name] = formatted
            
            if reel_urls:
                self._save_reels(conv_dir, conv_name, reel_urls)
            print("💾 Saving...")
            self._save_text(conv_dir, conv_name, formatted)
            self._save_json(conv_dir, conv_name, formatted, thread)
            self._save_html(conv_dir, conv_name, formatted, thread)
            
            text_c = sum(1 for m in formatted if m['type'] == 'text' and m['text'])
            media_c = sum(1 for m in formatted if m.get('media_files'))
            reel_c = sum(1 for m in formatted if m.get('reel_url'))
            voice_c = sum(1 for m in formatted if m['type'] == 'voice_media')
            
            print(f"✅ Done! {len(formatted)} msgs | 💬{text_c} 📷{media_c} 📽️{reel_c} 🎤{voice_c}")
            return True
        except Exception as e:
            print(f"❌ Error: {e}")
            return False
    
    def _process_message(self, msg, conv_name):
        try:
            sender = self.get_username_safe(msg.user_id)
            timestamp = msg.timestamp.isoformat() if msg.timestamp else ""
            dt = msg.timestamp if msg.timestamp else datetime.now()
            hour = dt.hour
            day = dt.strftime("%A")
            date_str = dt.strftime("%Y-%m-%d")
            
            data = {"id": msg.id, "timestamp": timestamp, "hour": hour, "day": day, "date": date_str, "sender_username": sender, "type": msg.item_type, "text": "", "media_files": [], "url": "", "reel_url": "", "replied_to": None, "reactions": []}
            
            if msg.item_type == "xma_clip":
                data["text"] = "📽️ Reel"
                if hasattr(msg, 'xma_share') and msg.xma_share and hasattr(msg.xma_share, 'preview_url'):
                    reel_url = self.extract_reel_url_from_preview(msg.xma_share.preview_url)
                    if reel_url:
                        data["reel_url"] = reel_url
                        data["text"] = f"📽️ Reel: {reel_url}"
            elif msg.item_type == "generic_xma":
                data["text"] = "📎 Content"
                if hasattr(msg, 'generic_xma') and msg.generic_xma:
                    items = msg.generic_xma if isinstance(msg.generic_xma, list) else [msg.generic_xma]
                    for item in items:
                        if hasattr(item, 'preview_url') and item.preview_url:
                            reel_url = self.extract_reel_url_from_preview(item.preview_url)
                            if reel_url:
                                data["reel_url"] = reel_url
                                data["text"] = f"📽️ Reel: {reel_url}"
                                break
            elif msg.item_type in ["media_share", "raven_media"]:
                try:
                    if hasattr(msg, 'media_share') and msg.media_share:
                        media = msg.media_share
                        if hasattr(media, 'caption_text') and media.caption_text:
                            data["text"] = media.caption_text
                        if hasattr(media, 'code') and media.code:
                            data["reel_url"] = f"https://www.instagram.com/p/{media.code}/"
                            if not data["text"]:
                                data["text"] = f"📷 {data['reel_url']}"
                        media_urls = []
                        if hasattr(media, 'video_url') and media.video_url:
                            media_urls.append(('video', media.video_url))
                        elif hasattr(media, 'image_url') and media.image_url:
                            media_urls.append(('image', media.image_url))
                        for mtype, url in media_urls:
                            path = self.download_media(url, conv_name, msg.id, mtype)
                            if path:
                                data["media_files"].append(path)
                except:
                    data["text"] = "📷 Media"
            elif msg.item_type == "text":
                data["text"] = msg.text if msg.text else ""
            elif msg.item_type == "link":
                try:
                    if hasattr(msg, 'link') and msg.link:
                        data["text"] = msg.link.get('text', 'Link')
                        data["url"] = msg.link.get('url', '')
                except:
                    data["text"] = "🔗 Link"
            elif msg.item_type == "voice_media":
                data["text"] = "🎤 Voice"
                try:
                    if hasattr(msg, 'voice_media') and hasattr(msg.voice_media, 'url'):
                        path = self.download_media(msg.voice_media.url, conv_name, msg.id, "voice")
                        if path:
                            data["media_files"].append(path)
                except:
                    pass
            elif msg.item_type == "clip":
                try:
                    if hasattr(msg, 'clip') and msg.clip:
                        if hasattr(msg.clip, 'code') and msg.clip.code:
                            data["reel_url"] = f"https://www.instagram.com/reel/{msg.clip.code}/"
                            data["text"] = f"📽️ Reel: {data['reel_url']}"
                        if hasattr(msg.clip, 'clip_url') and msg.clip.clip_url:
                            path = self.download_media(msg.clip.clip_url, conv_name, msg.id, "video")
                            if path:
                                data["media_files"].append(path)
                except:
                    data["text"] = "🎬 Clip"
            elif msg.item_type == "reel_share":
                try:
                    if hasattr(msg, 'reel_share') and msg.reel_share:
                        if hasattr(msg.reel_share, 'code') and msg.reel_share.code:
                            data["reel_url"] = f"https://www.instagram.com/reel/{msg.reel_share.code}/"
                        data["text"] = f"📽️ Reel: {msg.reel_share.text}" if hasattr(msg.reel_share, 'text') and msg.reel_share.text else "📽️ Reel"
                except:
                    data["text"] = "📽️ Reel"
            elif msg.item_type == "story_share":
                data["text"] = "📖 Story"
            elif msg.item_type == "xma_profile":
                data["text"] = "👤 Profile"
            elif msg.item_type == "like":
                data["text"] = "❤️"
            elif msg.item_type == "action_log":
                try:
                    data["text"] = msg.action_log.description if hasattr(msg, 'action_log') and hasattr(msg.action_log, 'description') else "Group action"
                except:
                    data["text"] = "Group action"
            else:
                data["text"] = f"[{msg.item_type}]"
            
            try:
                if hasattr(msg, 'replied_to_message') and msg.replied_to_message:
                    replied = msg.replied_to_message
                    preview = ""
                    if hasattr(replied, 'text') and replied.text:
                        preview = replied.text[:100]
                    elif hasattr(replied, 'item_type'):
                        preview = {"media_share": "📷 Media", "like": "❤️", "reel_share": "📽️ Reel", "clip": "🎬 Clip", "voice_media": "🎤 Voice"}.get(replied.item_type, f"[{replied.item_type}]")
                    if preview:
                        data["replied_to"] = {"message_id": replied.id, "preview": preview}
            except:
                pass
            
            try:
                if hasattr(msg, 'reactions') and msg.reactions:
                    for r in msg.reactions:
                        try:
                            emoji = r.emoji if hasattr(r, 'emoji') else "❤️"
                            data["reactions"].append({"username": self.get_username_safe(r.user_id), "emoji": emoji})
                        except:
                            pass
            except:
                pass
            
            # Extract words for analytics
            if data["text"] and data["type"] == "text":
                words = re.findall(r'\b\w+\b', data["text"].lower())
                data["_words"] = words
            
            return data
        except:
            return {"id": str(msg.id) if hasattr(msg, 'id') else "unknown", "timestamp": "", "hour": 0, "day": "", "date": "", "sender_username": "unknown", "type": "error", "text": "[Error]", "media_files": [], "reel_url": "", "url": "", "replied_to": None, "reactions": []}
    
    # ==================== FILE SAVERS ====================
    def _save_reels(self, directory, name, reel_urls):
        with open(directory / f"{name}_reels.txt", 'w', encoding='utf-8') as f:
            f.write(f"📽️ Reels from: {name}\n{'='*60}\n\n")
            for i, reel in enumerate(reel_urls, 1):
                try:
                    ts = datetime.fromisoformat(reel['timestamp']).strftime("%d %b %Y, %I:%M %p")
                except:
                    ts = reel['timestamp']
                f.write(f"[{i}] {ts} | @{reel['sender']}\n🔗 {reel['url']}\n{'-'*40}\n\n")
    
    def _save_text(self, directory, name, messages):
        with open(directory / f"{name}.txt", 'w', encoding='utf-8') as f:
            f.write(f"Mr.White Backup: {name}\n{'='*60}\n\n")
            for i, msg in enumerate(messages, 1):
                try:
                    ts = datetime.fromisoformat(msg['timestamp']).strftime("%d %b %Y, %I:%M %p")
                except:
                    ts = msg['timestamp']
                f.write(f"[{i}] {ts} | @{msg['sender_username']}\n")
                if msg['replied_to']:
                    f.write(f"↳ {msg['replied_to']['preview']}\n")
                if msg['text']:
                    f.write(f"{msg['text']}\n")
                if msg['reel_url']:
                    f.write(f"📽️ {msg['reel_url']}\n")
                if msg['media_files']:
                    for m in msg['media_files']:
                        f.write(f"📎 {m}\n")
                if msg['reactions']:
                    f.write(f"Reactions: {' '.join([r['emoji'] for r in msg['reactions']])}\n")
                f.write(f"{'-'*40}\n\n")
    
    def _save_json(self, directory, name, messages, thread):
        participants = []
        if hasattr(thread, 'users'):
            for uid in thread.users:
                participants.append(self.get_username_safe(uid))
        data = {"conversation": name, "thread_id": thread.id, "participants": participants, "message_count": len(messages), "export_date": datetime.now().isoformat(), "messages": messages}
        with open(directory / f"{name}.json", 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    def _save_html(self, directory, name, messages, thread):
        participants = []
        if hasattr(thread, 'users'):
            for uid in thread.users:
                participants.append(f"@{self.get_username_safe(uid)}")
        
        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Mr.White - {name}</title>
    <style>
        :root {{
            --bg: #ffffff;
            --surface: #fafafa;
            --border: #dbdbdb;
            --text: #262626;
            --text-secondary: #8e8e8e;
            --accent: #0095f6;
            --accent-hover: #0074cc;
            --gradient: linear-gradient(135deg, #1a1a2e, #16213e, #0f3460);
            --card-bg: #ffffff;
            --hover-bg: #f5f5f5;
            --reel-btn: #0095f6;
            --reel-btn-text: #ffffff;
        }}
        .dark-mode {{
            --bg: #0d0d0d;
            --surface: #1a1a1a;
            --border: #333333;
            --text: #e0e0e0;
            --text-secondary: #999999;
            --gradient: linear-gradient(135deg, #0a0a0a, #1a1a2e, #16213e);
            --card-bg: #1a1a1a;
            --hover-bg: #252525;
            --reel-btn: #1e90ff;
            --reel-btn-text: #ffffff;
        }}
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
            background: var(--bg);
            color: var(--text);
            transition: all 0.3s ease;
            padding: 20px;
        }}
        .container {{
            max-width: 900px;
            margin: 0 auto;
            background: var(--surface);
            border-radius: 16px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.15);
            overflow: hidden;
        }}
        .header {{
            background: var(--gradient);
            color: white;
            padding: 30px;
            position: relative;
        }}
        .header h1 {{ font-size: 24px; margin-bottom: 8px; }}
        .header .subtitle {{ opacity: 0.8; font-size: 13px; margin-top: 4px; }}
        .header .badge {{
            display: inline-block;
            background: rgba(255,255,255,0.15);
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 12px;
            margin-top: 8px;
        }}
        .theme-toggle {{
            position: absolute;
            top: 20px;
            right: 20px;
            background: rgba(255,255,255,0.2);
            border: none;
            color: white;
            padding: 8px 16px;
            border-radius: 20px;
            cursor: pointer;
            font-size: 16px;
            transition: all 0.3s;
        }}
        .theme-toggle:hover {{ background: rgba(255,255,255,0.3); }}
        .stats-bar {{
            display: flex;
            justify-content: space-around;
            padding: 20px;
            background: var(--card-bg);
            border-bottom: 1px solid var(--border);
            flex-wrap: wrap;
            gap: 10px;
        }}
        .stat {{ text-align: center; min-width: 80px; }}
        .stat-value {{ font-size: 24px; font-weight: 700; color: #0095f6; }}
        .stat-label {{ font-size: 11px; color: var(--text-secondary); text-transform: uppercase; letter-spacing: 1px; }}
        .messages {{ padding: 20px; }}
        .message {{
            padding: 16px 20px;
            border-bottom: 1px solid var(--border);
            transition: background 0.2s;
            background: var(--card-bg);
            margin-bottom: 4px;
            border-radius: 8px;
        }}
        .message:hover {{ background: var(--hover-bg); }}
        .msg-header {{ display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px; }}
        .sender {{ font-weight: 600; color: var(--text); font-size: 14px; }}
        .time {{ color: var(--text-secondary); font-size: 12px; }}
        .text {{ color: var(--text); line-height: 1.6; white-space: pre-wrap; word-wrap: break-word; font-size: 14px; }}
        .reply {{
            border-left: 3px solid #0095f6;
            padding: 8px 12px;
            margin-bottom: 8px;
            background: rgba(0,149,246,0.05);
            border-radius: 4px;
            color: var(--text-secondary);
            font-size: 12px;
        }}
        .media {{ margin: 10px 0; }}
        .media img {{ max-width: 100%; max-height: 400px; border-radius: 8px; cursor: pointer; }}
        .media video {{ max-width: 100%; max-height: 400px; border-radius: 8px; }}
        .reel-btn {{
            display: inline-block;
            background: var(--reel-btn);
            color: var(--reel-btn-text);
            padding: 8px 16px;
            border-radius: 20px;
            text-decoration: none;
            margin: 5px 0;
            font-size: 13px;
            font-weight: 500;
            transition: all 0.2s;
        }}
        .reel-btn:hover {{ background: var(--accent-hover); transform: translateY(-1px); }}
        .reactions {{ margin-top: 6px; font-size: 16px; letter-spacing: 2px; }}
        .search-box {{
            width: 100%;
            padding: 12px 20px;
            border: 2px solid var(--border);
            border-radius: 25px;
            font-size: 14px;
            background: var(--card-bg);
            color: var(--text);
            margin-bottom: 20px;
            outline: none;
            transition: border 0.3s;
        }}
        .search-box:focus {{ border-color: #0095f6; }}
        .highlight {{ background: #ffeb3b; color: #000; padding: 0 2px; border-radius: 2px; }}
        .footer {{
            text-align: center;
            padding: 20px;
            color: var(--text-secondary);
            font-size: 12px;
            border-top: 1px solid var(--border);
        }}
        .footer a {{ color: #0095f6; text-decoration: none; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <button class="theme-toggle" onclick="toggleTheme()">🌓</button>
            <h1>💬 {name}</h1>
            <div class="subtitle">Chat with: {", ".join(participants) if participants else "Unknown"}</div>
            <div class="badge">Mr.White Backup • {len(messages)} messages</div>
        </div>
        <div class="stats-bar">
            <div class="stat"><div class="stat-value" id="totalMsgs">{len(messages)}</div><div class="stat-label">Total</div></div>
            <div class="stat"><div class="stat-value" id="textMsgs">0</div><div class="stat-label">💬 Text</div></div>
            <div class="stat"><div class="stat-value" id="mediaMsgs">0</div><div class="stat-label">📷 Media</div></div>
            <div class="stat"><div class="stat-value" id="reelMsgs">0</div><div class="stat-label">📽️ Reels</div></div>
            <div class="stat"><div class="stat-value" id="voiceMsgs">0</div><div class="stat-label">🎤 Voice</div></div>
        </div>
        <div class="messages">
            <input type="text" class="search-box" placeholder="🔍 Search messages..." oninput="searchMessages(this.value)">
            <div id="messageList">
"""
        
        for msg in messages:
            try:
                ts = datetime.fromisoformat(msg['timestamp']).strftime("%d %b %Y, %I:%M %p")
            except:
                ts = ""
            
            msg_type = msg.get('type', '')
            html += f"""
                <div class="message" data-type="{msg_type}" data-text="{msg.get('text', '').lower().replace(chr(34), '&quot;')}">
                    <div class="msg-header">
                        <span class="sender">@{msg['sender_username']}</span>
                        <span class="time">{ts}</span>
                    </div>"""
            
            if msg['replied_to']:
                html += f'\n                    <div class="reply">↳ {msg["replied_to"]["preview"]}</div>'
            
            if msg['text']:
                html += f'\n                    <div class="text">{msg["text"]}</div>'
            
            if msg['reel_url']:
                html += f'\n                    <a href="{msg["reel_url"]}" class="reel-btn" target="_blank">📽️ Open</a>'
            
            if msg['media_files']:
                html += '\n                    <div class="media">'
                for media_file in msg['media_files']:
                    if media_file.lower().endswith(('.jpg', '.jpeg', '.png', '.gif')):
                        html += f'\n                        <img src="{media_file}" alt="Media" loading="lazy">'
                    elif media_file.lower().endswith(('.mp4', '.mov')):
                        html += f'\n                        <video controls preload="metadata"><source src="{media_file}" type="video/mp4"></video>'
                    else:
                        html += f'\n                        <div><a href="{media_file}">📎 Download</a></div>'
                html += '\n                    </div>'
            
            if msg['reactions']:
                html += f'\n                    <div class="reactions">{" ".join([r["emoji"] for r in msg["reactions"]])}</div>'
            
            html += '\n                </div>'
        
        html += """
            </div>
        </div>
        <div class="footer">
            Backed up with <a href="#">Mr.White</a> by anharhussan • {date}
        </div>
    </div>
    <script>
        function toggleTheme() {{
            document.body.classList.toggle('dark-mode');
            localStorage.setItem('mrwhite-theme', document.body.classList.contains('dark-mode') ? 'dark' : 'light');
        }}
        // Load saved theme
        if (localStorage.getItem('mrwhite-theme') === 'dark') {{
            document.body.classList.add('dark-mode');
        }}
        function searchMessages(query) {{
            const messages = document.querySelectorAll('.message');
            const lowerQuery = query.toLowerCase();
            let visible = 0;
            messages.forEach(msg => {{
                const text = msg.getAttribute('data-text') || '';
                if (lowerQuery === '' || text.includes(lowerQuery)) {{
                    msg.style.display = '';
                    visible++;
                }} else {{
                    msg.style.display = 'none';
                }}
            }});
            document.getElementById('totalMsgs').textContent = visible;
        }}
        // Update stats
        document.addEventListener('DOMContentLoaded', function() {{
            const msgs = document.querySelectorAll('.message');
            let text=0, media=0, reel=0, voice=0;
            msgs.forEach(m => {{
                const type = m.getAttribute('data-type');
                if (type === 'text') text++;
                else if (type === 'media_share') media++;
                else if (type === 'xma_clip' || type === 'clip' || type === 'reel_share' || type === 'generic_xma') reel++;
                else if (type === 'voice_media') voice++;
            }});
            document.getElementById('textMsgs').textContent = text;
            document.getElementById('mediaMsgs').textContent = media;
            document.getElementById('reelMsgs').textContent = reel;
            document.getElementById('voiceMsgs').textContent = voice;
        }});
    </script>
</body>
</html>"""
        
        html = html.replace('{date}', datetime.now().strftime('%d %b %Y'))
        
        with open(directory / f"{name}.html", 'w', encoding='utf-8') as f:
            f.write(html)
    
    # ==================== ANALYTICS DASHBOARD ====================
    # mrwhite.py
# ... (everything above stays the same until line ~766)

    def generate_analytics_dashboard(self):
        """Generate full analytics dashboard"""
        if not self.all_messages:
            print("\n⚠ No data for analytics. Download some conversations first!")
            return
        
        print("\n📊 Generating analytics dashboard...")
        
        analytics_dir = self.backup_dir / "analytics"
        analytics_dir.mkdir(exist_ok=True)
        
        all_msgs = []
        for conv_name, msgs in self.all_messages.items():
            for msg in msgs:
                msg['_conversation'] = conv_name
                all_msgs.append(msg)
        
        # Calculate stats
        total_messages = len(all_msgs)
        conversations = len(self.all_messages)
        
        # Messages per conversation
        conv_counts = Counter(msg['_conversation'] for msg in all_msgs)
        
        # Messages by sender
        sender_counter = Counter(msg['sender_username'] for msg in all_msgs)
        top_senders = sender_counter.most_common(5)
        
        # Messages by hour (peak hours)
        hour_counts = Counter(msg.get('hour', 0) for msg in all_msgs)
        peak_hour = hour_counts.most_common(1)[0] if hour_counts else (0, 0)
        
        # Messages by day of week
        day_counts = Counter(msg.get('day', '') for msg in all_msgs)
        
        # Messages by date (timeline)
        date_counts = Counter(msg.get('date', '') for msg in all_msgs)
        dates_sorted = sorted(date_counts.items())
        
        # Message types
        type_counts = Counter(msg['type'] for msg in all_msgs)
        
        # Word frequency (from text messages)
        all_words = []
        for msg in all_msgs:
            if msg['type'] == 'text' and msg.get('_words'):
                all_words.extend(msg['_words'])
        
        # Filter common words
        stop_words = {'the', 'a', 'an', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might', 'can', 'shall', 'i', 'me', 'my', 'we', 'our', 'you', 'your', 'he', 'she', 'it', 'they', 'them', 'this', 'that', 'these', 'those', 'to', 'of', 'in', 'for', 'on', 'with', 'at', 'by', 'from', 'and', 'or', 'but', 'not', 'no', 'yes', 'so', 'if', 'just', 'like', 'very', 'really', 'ok', 'okay', 'hmm', 'oh', 'ah', 'ha', 'haha'}
        filtered_words = [w for w in all_words if w not in stop_words and len(w) > 1]
        top_words = Counter(filtered_words).most_common(20)
        
        # Generate HTML dashboard
        dashboard_html = self._generate_dashboard_html(
            total_messages, conversations, conv_counts, top_senders,
            hour_counts, peak_hour, day_counts, dates_sorted,
            type_counts, top_words, all_msgs
        )
        
        with open(analytics_dir / "dashboard.html", 'w', encoding='utf-8') as f:
            f.write(dashboard_html)
        
        # Save stats as JSON - FIXED: use sender_counter instead of top_senders
        stats_data = {
            "total_messages": total_messages,
            "conversations": conversations,
            "conv_counts": dict(conv_counts.most_common()),
            "top_senders": dict(sender_counter.most_common(10)),  # FIXED
            "peak_hour": peak_hour[0],
            "hourly_distribution": {str(k): v for k, v in sorted(hour_counts.items())},
            "daily_distribution": {str(k): v for k, v in day_counts.items()},
            "message_types": dict(type_counts),
            "top_words": dict(top_words),
            "timeline": dict(dates_sorted[-30:] if len(dates_sorted) > 30 else dates_sorted)
        }
        
        with open(analytics_dir / "stats.json", 'w', encoding='utf-8') as f:
            json.dump(stats_data, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Dashboard saved: {analytics_dir / 'dashboard.html'}")
        print(f"✅ Stats saved: {analytics_dir / 'stats.json'}")

    def _generate_dashboard_html(self, total, convs, conv_counts, top_senders, hour_counts, peak_hour, day_counts, dates_sorted, type_counts, top_words, all_msgs):
        """Generate beautiful analytics dashboard HTML"""
        
        # Peak hours chart data
        hours_labels = list(range(24))
        hours_data = [hour_counts.get(h, 0) for h in hours_labels]
        max_hour_val = max(hours_data) if hours_data else 1
        
        # Day chart data
        days_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        days_data = [day_counts.get(d, 0) for d in days_order]
        max_day_val = max(days_data) if days_data else 1
        
        # Timeline data (last 30 days)
        timeline = dict(dates_sorted[-30:] if len(dates_sorted) > 30 else dates_sorted)
        
        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Mr.White Analytics Dashboard</title>
    <style>
        :root {{
            --bg: #0d1117;
            --surface: #161b22;
            --border: #30363d;
            --text: #c9d1d9;
            --text-secondary: #8b949e;
            --accent: #58a6ff;
            --accent2: #3fb950;
            --accent3: #d2a8ff;
            --accent4: #f78166;
            --accent5: #ffa657;
        }}
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: var(--bg);
            color: var(--text);
            padding: 20px;
            line-height: 1.6;
        }}
        .container {{ max-width: 1200px; margin: 0 auto; }}
        .header {{
            text-align: center;
            padding: 40px 20px;
            background: linear-gradient(135deg, #1a1a2e, #16213e);
            border-radius: 16px;
            margin-bottom: 30px;
            border: 1px solid var(--border);
        }}
        .header h1 {{ font-size: 36px; color: var(--accent3); }}
        .header p {{ color: var(--text-secondary); font-size: 14px; margin-top: 8px; }}
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 16px;
            margin-bottom: 30px;
        }}
        .stat-card {{
            background: var(--surface);
            border: 1px solid var(--border);
            border-radius: 12px;
            padding: 20px;
            text-align: center;
        }}
        .stat-card .value {{
            font-size: 32px;
            font-weight: 700;
            background: linear-gradient(135deg, var(--accent), var(--accent3));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }}
        .stat-card .label {{ color: var(--text-secondary); font-size: 12px; text-transform: uppercase; letter-spacing: 1px; }}
        .section {{
            background: var(--surface);
            border: 1px solid var(--border);
            border-radius: 12px;
            padding: 24px;
            margin-bottom: 20px;
        }}
        .section h2 {{
            color: var(--accent3);
            margin-bottom: 16px;
            font-size: 20px;
        }}
        .bar-chart {{ position: relative; }}
        .bar-row {{
            display: flex;
            align-items: center;
            margin-bottom: 8px;
        }}
        .bar-label {{ width: 100px; font-size: 12px; color: var(--text-secondary); text-align: right; padding-right: 10px; }}
        .bar-track {{ flex: 1; background: var(--border); border-radius: 4px; height: 24px; position: relative; overflow: hidden; }}
        .bar-fill {{
            height: 100%;
            border-radius: 4px;
            background: linear-gradient(90deg, var(--accent), var(--accent3));
            transition: width 0.5s ease;
            min-width: 2px;
        }}
        .bar-value {{ width: 60px; font-size: 12px; padding-left: 10px; color: var(--text); }}
        .table {{
            width: 100%;
            border-collapse: collapse;
        }}
        .table th, .table td {{
            padding: 10px 16px;
            text-align: left;
            border-bottom: 1px solid var(--border);
            font-size: 13px;
        }}
        .table th {{ color: var(--text-secondary); text-transform: uppercase; font-size: 11px; letter-spacing: 1px; }}
        .table tr:hover {{ background: rgba(255,255,255,0.02); }}
        .badge {{
            display: inline-block;
            padding: 2px 10px;
            border-radius: 12px;
            font-size: 11px;
            font-weight: 500;
        }}
        .badge-blue {{ background: rgba(88,166,255,0.15); color: var(--accent); }}
        .badge-green {{ background: rgba(63,185,80,0.15); color: var(--accent2); }}
        .badge-orange {{ background: rgba(255,165,87,0.15); color: var(--accent5); }}
        .badge-pink {{ background: rgba(210,168,255,0.15); color: var(--accent3); }}
        .timeline-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(12px, 1fr));
            gap: 2px;
        }}
        .timeline-cell {{
            aspect-ratio: 1;
            border-radius: 2px;
            background: var(--border);
            cursor: pointer;
        }}
        .footer {{
            text-align: center;
            padding: 30px;
            color: var(--text-secondary);
            font-size: 12px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>💎 Mr.White Analytics</h1>
            <p>Instagram DM Backup & Analytics by anharhussan</p>
            <p>Generated: {datetime.now().strftime('%d %b %Y, %I:%M %p')}</p>
        </div>
        
        <!-- Key Stats -->
        <div class="stats-grid">
            <div class="stat-card">
                <div class="value">{total:,}</div>
                <div class="label">Total Messages</div>
            </div>
            <div class="stat-card">
                <div class="value">{convs}</div>
                <div class="label">Conversations</div>
            </div>
            <div class="stat-card">
                <div class="value">{len(top_senders)}</div>
                <div class="label">Unique Senders</div>
            </div>
            <div class="stat-card">
                <div class="value">{peak_hour[0]:02d}:00</div>
                <div class="label">Peak Hour</div>
            </div>
        </div>
        
        <!-- Peak Hours Chart -->
        <div class="section">
            <h2>⏰ Peak Activity Hours</h2>
            <div class="bar-chart">
"""
        for h in range(24):
            val = hours_data[h]
            pct = (val / max_hour_val * 100) if max_hour_val > 0 else 0
            period = "AM" if h < 12 else "PM"
            hour_12 = h if h <= 12 else h - 12
            if hour_12 == 0: hour_12 = 12
            html += f'                <div class="bar-row"><div class="bar-label">{hour_12} {period}</div><div class="bar-track"><div class="bar-fill" style="width:{pct:.0f}%"></div></div><div class="bar-value">{val}</div></div>\n'
        
        html += """            </div>
        </div>
        
        <!-- Messages by Day -->
        <div class="section">
            <h2>📅 Messages by Day</h2>
            <div class="bar-chart">
"""
        for i, day in enumerate(days_order):
            val = days_data[i]
            pct = (val / max_day_val * 100) if max_day_val > 0 else 0
            html += f'                <div class="bar-row"><div class="bar-label">{day[:3]}</div><div class="bar-track"><div class="bar-fill" style="width:{pct:.0f}%"></div></div><div class="bar-value">{val}</div></div>\n'
        
        html += """            </div>
        </div>
        
        <!-- Top Conversations -->
        <div class="section">
            <h2>💬 Top Conversations</h2>
            <table class="table">
                <thead><tr><th>Conversation</th><th>Messages</th><th>%</th></tr></thead>
                <tbody>
"""
        for conv, count in conv_counts.most_common(10):
            pct = (count / total * 100) if total > 0 else 0
            html += f'                    <tr><td>{conv}</td><td>{count:,}</td><td><span class="badge badge-blue">{pct:.1f}%</span></td></tr>\n'
        
        html += """                </tbody>
            </table>
        </div>
        
        <!-- Top Senders -->
        <div class="section">
            <h2>👤 Most Active People</h2>
            <table class="table">
                <thead><tr><th>User</th><th>Messages</th><th>%</th></tr></thead>
                <tbody>
"""
        for sender, count in top_senders[:10]:
            pct = (count / total * 100) if total > 0 else 0
            html += f'                    <tr><td>@{sender}</td><td>{count:,}</td><td><span class="badge badge-green">{pct:.1f}%</span></td></tr>\n'
        
        html += """                </tbody>
            </table>
        </div>
        
        <!-- Top Words -->
        <div class="section">
            <h2>🔤 Most Used Words</h2>
            <table class="table">
                <thead><tr><th>Word</th><th>Count</th></tr></thead>
                <tbody>
"""
        for word, count in top_words:
            html += f'                    <tr><td>{word}</td><td>{count:,}</td></tr>\n'
        
        html += f"""                </tbody>
            </table>
        </div>
        
        <!-- Message Types -->
        <div class="section">
            <h2>📊 Message Types</h2>
            <table class="table">
                <thead><tr><th>Type</th><th>Count</th><th>%</th></tr></thead>
                <tbody>
"""
        type_labels = {'text': '💬 Text', 'media_share': '📷 Media', 'xma_clip': '📽️ Reel', 'clip': '🎬 Clip', 'reel_share': '📽️ Reel Share', 'voice_media': '🎤 Voice', 'like': '❤️ Like', 'link': '🔗 Link', 'generic_xma': '📎 Content'}
        for mtype, count in type_counts.most_common():
            label = type_labels.get(mtype, mtype)
            pct = (count / total * 100) if total > 0 else 0
            html += f'                    <tr><td>{label}</td><td>{count:,}</td><td><span class="badge badge-pink">{pct:.1f}%</span></td></tr>\n'
        
        html += """                </tbody>
            </table>
        </div>
        
        <div class="footer">
            <p>💎 Mr.White by <strong>anharhussan</strong> | "I am the one who backs up."</p>
        </div>
    </div>
</body>
</html>"""
        
        return html
    
    # ==================== SEARCH TOOL ====================
    def search_backups(self, query):
        """Search across all backed up conversations"""
        print(f"\n🔍 Searching for: '{query}'")
        print("=" * 60)
        
        results = []
        for conv_dir in self.backup_dir.iterdir():
            if conv_dir.is_dir() and conv_dir.name != "analytics":
                json_file = conv_dir / f"{conv_dir.name}.json"
                if json_file.exists():
                    try:
                        with open(json_file, 'r', encoding='utf-8') as f:
                            data = json.load(f)
                        for msg in data.get('messages', []):
                            text = msg.get('text', '') + ' ' + msg.get('reel_url', '') + ' ' + msg.get('url', '')
                            if query.lower() in text.lower():
                                results.append({
                                    'conversation': conv_dir.name,
                                    'sender': msg.get('sender_username', ''),
                                    'timestamp': msg.get('timestamp', ''),
                                    'text': msg.get('text', '')[:200],
                                    'reel_url': msg.get('reel_url', ''),
                                    'url': msg.get('url', '')
                                })
                    except:
                        pass
        
        if results:
            print(f"Found {len(results)} results:\n")
            for i, r in enumerate(results[:50], 1):
                try:
                    ts = datetime.fromisoformat(r['timestamp']).strftime("%d %b %Y, %I:%M %p")
                except:
                    ts = r['timestamp']
                print(f"[{i}] 📱 {r['conversation']} | {ts}")
                print(f"    👤 @{r['sender']}")
                print(f"    💬 {r['text'][:150]}{'...' if len(r['text']) > 150 else ''}")
                if r['reel_url']:
                    print(f"    📽️ {r['reel_url']}")
                if r['url'] and r['url'] != r['reel_url']:
                    print(f"    🔗 {r['url']}")
                print()
        else:
            print("No results found.")
        
        return results
    
    # ==================== UTILITY ====================
    def create_backup_archive(self):
        """Create ZIP archive of all backups"""
        print("\n📦 Creating backup archive...")
        archive_path = self.backup_dir.parent / f"mrwhite_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip"
        
        with zipfile.ZipFile(archive_path, 'w', zipfile.ZIP_DEFLATED) as zf:
            for root, dirs, files in os.walk(self.backup_dir):
                for file in files:
                    file_path = Path(root) / file
                    arc_name = file_path.relative_to(self.backup_dir.parent)
                    zf.write(file_path, arc_name)
        
        size_mb = archive_path.stat().st_size / (1024 * 1024)
        print(f"✅ Archive created: {archive_path} ({size_mb:.1f} MB)")
        return archive_path
    
    def _sanitize(self, name):
        if not name:
            return "Unnamed_Chat"
        return re.sub(r'[<>:"/\\|?*]', '_', name)[:100].strip()


# ==================== HEISENBERG INTRO ====================
def breaking_bad_intro():
    print(BANNER)
    print("\n🧪 A cloud of smoke rises...")
    print("👨‍🔬 A bald man in a pork pie hat steps forward...")
    time.sleep(0.5)
    name = input("\n💀 SAY MY NAME: ").strip()
    if name.lower() == "anharhussan":
        print("\n😤 YOU'RE GODDAMN RIGHT.")
        time.sleep(0.8)
        print("\n💎 Mr.White is ready. Let's cook.")
        return True
    else:
        print(f"\n🤨 {name}? You're not the one who knocks.")
        return False


# ==================== MAIN MENU ====================
if __name__ == "__main__":
    if not breaking_bad_intro():
        exit()
    
    mr_white = MrWhite(backup_dir="mrwhite_backups")
    
    # Login first
    success, username = mr_white.login()
    if not success:
        print("\n💀 Batch contaminated. Abort.")
        exit()
    
    while True:
        print("\n" + "=" * 50)
        print("💎  MR.WHITE MAIN MENU")
        print("=" * 50)
        print("  1. 📥 Download conversations")
        print("  2. 📊 Generate analytics dashboard")
        print("  3. 🔍 Search through backups")
        print("  4. 📦 Create ZIP archive")
        print("  5. 🚪 Exit")
        print("=" * 50)
        
        choice = input("\n🎯 Select option: ").strip()
        
        if choice == '1':
            selected = mr_white.list_conversations()
            if selected:
                print("\n" + "=" * 50)
                print("⚗️  COOKING...")
                print("=" * 50)
                success_count = 0
                for thread in selected:
                    if mr_white.process_conversation(thread):
                        success_count += 1
                    time.sleep(2)
                print(f"\n💎 {success_count}/{len(selected)} batches cooked perfectly.")
                print(f"📁 Product: {mr_white.backup_dir.absolute()}")
        
        elif choice == '2':
            mr_white.generate_analytics_dashboard()
        
        elif choice == '3':
            query = input("\n🔍 Enter search term: ").strip()
            if query:
                mr_white.search_backups(query)
        
        elif choice == '4':
            mr_white.create_backup_archive()
        
        elif choice == '5':
            print("\n💎 No half measures. See you next cook.")
            break
        
        else:
            print("\n⚠ Invalid option!")
