from telethon.sync import TelegramClient, events
from telethon.tl.types import InputPeerChannel
import asyncio
import re
import os
import time

# ===== CONFIGURATION ===== #
API_ID = xxxxxxxx
API_HASH = "xxxxxxxxxxxxxxxxxxxxxxxxxxxx"
BOT_TOKEN = "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
ADMIN_ID = xxxxxxxxxxxxx
TARGET_GROUP_ID = xxxxxxxxxxx

# ===== BOT SETUP ===== #
bot = TelegramClient('message_cloner_bot', API_ID, API_HASH).start(bot_token=BOT_TOKEN)

# Global variables
remaining_links = []
is_processing = True  # Flag to control processing
current_position = 0  # Track current processing position
total_links = 0  # Track total links initially provided
custom_caption = None  # Stores the custom caption
caption_count = 0  # Number of remaining messages to apply caption to

def extract_links(text):
    # Only supports format: https://t.me/channelname/123
    pattern = r'https?://t\.me/([^/]+)/(\d+)'
    return re.findall(pattern, text)

async def is_admin(event):
    return event.sender_id == ADMIN_ID

@bot.on(events.NewMessage(pattern='/start'))
async def start(event):
    if not await is_admin(event):
        await event.reply("🚫 Access Denied!")
        return
    
    await event.reply("""
    🤖 **Media Cloner Bot**
    /clone [link] - Forward media (images, videos, GIFs) from links
    /remain - Get remaining links as a text file
    /stopnow - Pause processing
    /startnow - Resume processing
    /list - Show current queue lists
    /clean - Clear all queued links and stop immediately
    /skip N - Skip N links from the queue
    /cap [text] - Add caption to next media (or /cap N [text] for N media)
    /capstop - Stop adding captions
    /help - Show this message
    Or send a .txt file containing multiple Telegram post links
    """)

@bot.on(events.NewMessage(pattern='/help'))
async def help_command(event):
    if not await is_admin(event):
        return
    await start(event)

@bot.on(events.NewMessage(pattern='/stopnow'))
async def stop_command(event):
    if not await is_admin(event):
        return
    global is_processing
    is_processing = False
    await event.reply("⏸ Processing paused. Use /startnow to resume.")

@bot.on(events.NewMessage(pattern='/startnow'))
async def start_command(event):
    if not await is_admin(event):
        return
    global is_processing
    is_processing = True
    await event.reply("▶ Processing resumed.")

@bot.on(events.NewMessage(pattern='/list'))
async def list_command(event):
    if not await is_admin(event):
        return
    if not remaining_links:
        await event.reply("✅ No links in queue - all done!")
        return
    
    message = f"📋 Current Queue (Position: {current_position+1}/{total_links}):\n\n"
    for i, (channel, msg_id) in enumerate(remaining_links[:50], current_position+1):
        message += f"{i}. https://t.me/{channel}/{msg_id}\n"
    
    if len(remaining_links) > 50:
        message += f"\n...and {len(remaining_links)-50} more links."
    
    await event.reply(message)

@bot.on(events.NewMessage(pattern='/clean'))
async def clean_command(event):
    if not await is_admin(event):
        return
    global remaining_links, is_processing, current_position, total_links, custom_caption, caption_count
    remaining_links = []
    is_processing = False
    current_position = 0
    total_links = 0
    custom_caption = None
    caption_count = 0
    await event.reply("🧹 Queue cleared and processing stopped.")

@bot.on(events.NewMessage(pattern=r'/skip\s+(\d+)'))
async def skip_command(event):
    if not await is_admin(event):
        return
    
    try:
        skip_count = int(event.pattern_match.group(1))
        if skip_count <= 0:
            await event.reply("❌ Please provide a positive number to skip.")
            return
            
        global remaining_links, current_position, total_links
        
        if skip_count >= len(remaining_links):
            # If skip count exceeds remaining links, mark all as skipped
            skipped_count = len(remaining_links)
            remaining_links = []
            current_position = total_links
            await event.reply(f"⏭ Skipped all remaining {skipped_count} links. Processing complete!")
        else:
            # Skip the specified number of links
            remaining_links = remaining_links[skip_count:]
            current_position += skip_count
            await event.reply(f"⏭ Skipped {skip_count} links. Now at position {current_position+1}/{total_links}")
            
            # Show the next few links
            if remaining_links:
                preview = "Next links to process:\n"
                for i, (channel, msg_id) in enumerate(remaining_links[:3], current_position+1):
                    preview += f"{i}. https://t.me/{channel}/{msg_id}\n"
                if len(remaining_links) > 3:
                    preview += f"...and {len(remaining_links)-3} more"
                await event.reply(preview)
            
    except Exception as e:
        await event.reply(f"❌ Error: {str(e)}")

async def save_remaining_links(event):
    if not remaining_links:
        await event.reply("✅ No remaining links - all done!")
        return
    
    # Create a temporary file
    temp_file = "remaining_links.txt"
    with open(temp_file, 'w') as f:
        for channel, msg_id in remaining_links:
            f.write(f"https://t.me/{channel}/{msg_id}\n")
    
    # Send the file
    await bot.send_file(
        event.chat_id,
        temp_file,
        caption=f"📄 Remaining links: {len(remaining_links)} (Position: {current_position+1}/{total_links})"
    )
    
    # Clean up
    os.remove(temp_file)

@bot.on(events.NewMessage(pattern='/remain'))
async def remain_command(event):
    if not await is_admin(event):
        return
    await save_remaining_links(event)

@bot.on(events.NewMessage(pattern=r'/cap(\s+\d+)?\s*(.*)'))
async def set_caption(event):
    if not await is_admin(event):
        return
    
    global custom_caption, caption_count
    
    match = event.pattern_match
    count_part = match.group(1)
    caption_text = match.group(2).strip()
    
    if count_part:
        try:
            caption_count = int(count_part.strip())
            if caption_count <= 0:
                await event.reply("❌ Please provide a positive number for caption count.")
                return
        except ValueError:
            await event.reply("❌ Invalid number format for caption count.")
            return
    else:
        # If no count specified, set to unlimited (until /capstop)
        caption_count = -1
    
    if not caption_text:
        # If no caption provided, ask for it
        await event.reply("📝 Please send the caption text you want to add:")
        
        @bot.on(events.NewMessage(func=lambda e: e.sender_id == ADMIN_ID))
        async def wait_for_caption_text(caption_event):
            global custom_caption
            custom_caption = caption_event.text
            await caption_event.reply(f"✅ Caption set for {'next ' + str(caption_count) + ' media' if caption_count > 0 else 'all future media'}:\n{custom_caption}")
            bot.remove_event_handler(wait_for_caption_text)
    else:
        custom_caption = caption_text
        await event.reply(f"✅ Caption set for {'next ' + str(caption_count) + ' media' if caption_count > 0 else 'all future media'}:\n{custom_caption}")

@bot.on(events.NewMessage(pattern='/capstop'))
async def stop_caption(event):
    if not await is_admin(event):
        return
    
    global custom_caption, caption_count
    custom_caption = None
    caption_count = 0
    await event.reply("🛑 Caption feature stopped. No more captions will be added.")

async def process_links(event, links):
    global remaining_links, current_position, total_links, custom_caption, caption_count
    
    if not links:
        await event.reply("❌ No valid links found!")
        return

    remaining_links = links.copy()
    total_links = len(links)
    current_position = 0
    await event.reply(f"🔍 Found {total_links} links. Processing only media messages...")
    
    success_count = 0
    skipped_count = 0
    batch_size = 50
    delay_between_messages = 6  # seconds
    delay_between_batches = 180  # 3 minutes in seconds

    while current_position < total_links and remaining_links:
        # Check if processing is paused
        while not is_processing:
            await asyncio.sleep(5)  # Check every 5 seconds if processing is resumed
        
        channel, msg_id = remaining_links[0]
        
        try:
            # Show which link is being processed
            await event.reply(f"🔍 Checking ({current_position+1}/{total_links}): https://t.me/{channel}/{msg_id}")
            
            entity = await bot.get_entity(channel)
            msg = await bot.get_messages(entity, ids=int(msg_id))
            
            if msg:
                # Check if message has media (image, video, GIF)
                if msg.media:
                    # Determine if we should add caption
                    use_caption = custom_caption is not None and (caption_count > 0 or caption_count == -1)
                    
                    # Forward media with or without caption
                    await bot.send_file(
                        TARGET_GROUP_ID,
                        msg.media,
                        caption=custom_caption if use_caption else "",
                        silent=True,
                        link_preview=False
                    )
                    
                    # Update caption count if applicable
                    if use_caption and caption_count > 0:
                        caption_count -= 1
                        if caption_count == 0:
                            custom_caption = None
                            await event.reply("ℹ️ Caption limit reached. No more captions will be added.")
                    
                    success_count += 1
                    await event.reply(f"✅ Cloned media {current_position+1}/{total_links}" + (" (with caption)" if use_caption else ""))
                    
                    # Auto send /remain after every 10 successful clones
                    if success_count % 10 == 0:
                        await save_remaining_links(event)
                        await asyncio.sleep(5)  # Small delay before continuing
                    
                    # Check if we've processed a batch of 50
                    if success_count % batch_size == 0:
                        await event.reply(f"⏳ Processed {success_count} media messages. Waiting 3 minutes before continuing...")
                        await asyncio.sleep(delay_between_batches)
                    else:
                        # Wait 6 seconds between messages
                        await asyncio.sleep(delay_between_messages)
                else:
                    skipped_count += 1
                    await event.reply(f"⏩ Skipped text message {current_position+1}/{total_links}")
                    # Wait 2 seconds before checking next message
                    await asyncio.sleep(2)

            # Remove the processed link and update position
            remaining_links.pop(0)
            current_position += 1

        except Exception as e:
            await event.reply(f"❌ Error processing link {current_position+1}: {str(e)}")
            # Remove the problematic link and continue
            remaining_links.pop(0)
            current_position += 1
            continue

    await event.reply(f"🏁 Processing complete!\nSuccessfully cloned {success_count} media messages.\nSkipped {skipped_count} text messages.")

@bot.on(events.NewMessage(pattern='/clone'))
async def clone_message(event):
    if not await is_admin(event):
        return

    links = extract_links(event.raw_text)
    await process_links(event, links)

@bot.on(events.NewMessage)
async def handle_file_upload(event):
    if not await is_admin(event):
        return
    
    if event.file and event.file.name.endswith('.txt'):
        try:
            # Download the file
            temp_file = await event.download_media()
            
            # Read links from the file
            with open(temp_file, 'r') as f:
                content = f.read()
                links = extract_links(content)
                
            # Process the links
            await process_links(event, links)
            
            # Clean up
            os.remove(temp_file)
            
        except Exception as e:
            await event.reply(f"❌ Error processing file: {str(e)}")
            if 'temp_file' in locals() and os.path.exists(temp_file):
                os.remove(temp_file)

print("⚡ Bot running...")
bot.run_until_disconnected()
