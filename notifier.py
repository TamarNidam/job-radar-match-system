import requests

TOKEN = "8634110209:AAEzV5IShM472oDLc962PkGcrBIutEjdYRE"
CHAT_ID = "5680571658"

def send_telegram_notification(jobs):
    """
    Sends a beautifully formatted Telegram message with the approved jobs.
    """

    # Build the message text
    message = "CareerBot: New Recommended Jobs Found!\n\n"    
    for job in jobs:
        message += f"{job['title']}\n"
        message += f"Location: {job['location']}\n"
        message += f"Match Score:{job['score']}%\n"
        message += f"Best CV: {job['cv']}\n"
        message += f"Click to Apply: {job['apply_link']}\n"
        message += "---------\n"

    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    
    payload = {
        "chat_id": CHAT_ID,
        "text": message
    }
    
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        print("✅ [SUCCESS] Telegram notification sent successfully!")
    except Exception as e:
        print(f"❌ [ERROR] Failed to send Telegram notification: {e}")