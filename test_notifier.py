from notifier import send_telegram_notification

def run_notifier_test():
    print("=" * 50)
    print("🧪 STARTING TELEGRAM NOTIFIER TEST 🧪")
    print("=" * 50)

    # Creating fake "approved" jobs exactly as main.py will format them
    mock_approved_jobs = [
        {
            "title": "Senior Backend Engineer (Mock Job 1)",
            "location": "Raanana (Amdocs Site)",
            "score": 95,
            "cv": "high_scale_kafka",
            "apply_link": "https://jobs.amdocs.com/careers/apply?pid=12345"
        },
        {
            "title": "AI & Performance Expert (Mock Job 2)",
            "location": "Tel Aviv / Hybrid",
            "score": 88,
            "cv": "performance_ai",
            "apply_link": "https://jobs.amdocs.com/careers/apply?pid=67890"
        }
    ]

    print(f"Sending {len(mock_approved_jobs)} mock jobs to Telegram...")
    
    # Call the actual function
    try:
        send_telegram_notification(mock_approved_jobs)
        print("\n✅ Test finished! Please check your Telegram app.")
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        
if __name__ == "__main__":
    run_notifier_test()