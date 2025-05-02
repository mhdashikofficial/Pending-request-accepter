import logging
import asyncio
from pyrogram import Client, filters
from pyrogram.errors import FloodWait, PeerIdInvalid, RPCError

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('approve_bot.log')
    ]
)

API_ID =   # Replace with your API ID
API_HASH = ""  # Replace with your API hash

app = Client("user_account_session", api_id=API_ID, api_hash=API_HASH)

async def process_requests(chat_id):
    while True:
        try:
            # Use async generator to fetch join requests
            async for request in app.get_chat_join_requests(chat_id):
                try:
                    user_id = request.user.id
                    await app.approve_chat_join_request(chat_id, user_id)
                    logging.info(f"Approved: {user_id}")
                    await asyncio.sleep(0.2)  # Reduced delay for faster processing
                except PeerIdInvalid:
                    logging.error(f"Invalid peer ID for user ID: {user_id}, skipping.")
                    continue
                except FloodWait as e:
                    logging.warning(f"FloodWait encountered: Sleeping for {e.x} seconds.")
                    await asyncio.sleep(e.x)
                    continue  # Retry the same request after wait
                except RPCError as e:
                    if "USER_CHANNELS_TOO_MUCH" in str(e):
                        logging.warning(f"User {user_id} has too many channels. Skipping.")
                    else:
                        logging.error(f"RPCError for user {user_id}: {e}")
                    continue
                except Exception as e:
                    logging.error(f"Unexpected error processing user {user_id}: {e}")
                    continue

            # Short delay before checking for new requests again
            await asyncio.sleep(1)

        except Exception as e:
            logging.error(f"Error in main processing loop: {e}")
            await asyncio.sleep(10)  # Wait before retrying

@app.on_message(filters.command(["run", "approve"], prefixes=[".", "/"]))
async def approve(client, message):
    chat_id = message.chat.id
    try:
        await message.delete()
    except:
        pass
    
    # Start processing in the background
    asyncio.create_task(process_requests(chat_id))
    
    # Send temporary notification
    try:
        msg = await client.send_message(chat_id, "**Join Request Approver Started** ✅")
        await asyncio.sleep(5)
        await msg.delete()
    except:
        pass

@app.on_message(filters.command(["status"], prefixes=[".", "/"]))
async def status(client, message):
    try:
        msg = await client.send_message(message.chat.id, "**Bot is running!** 🚀")
        await asyncio.sleep(5)
        await msg.delete()
    except:
        pass

async def keep_alive():
    while True:
        await asyncio.sleep(3600)  # Just to keep the coroutine alive

async def main():
    await app.start()
    logging.info("Bot Started...")
    await keep_alive()

if __name__ == "__main__":
    try:
        app.run(main())
    except KeyboardInterrupt:
        logging.info("Bot stopped by user")
    except Exception as e:
        logging.error(f"Fatal error: {e}")
        # The script will actually stop here, but the while True loops above
        # ensure it keeps running for normal operation errors
