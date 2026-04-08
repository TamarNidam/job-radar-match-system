import os
from flask import json
from scrapers.microsoft import process_microsoft_jobs
from scrapers.amdox import process_amdocs_jobs
from analyzer import CareerBotAnalyzer
from notifier import send_telegram_notification
from datetime import datetime

CONFIG_FILE = "lastRun_config.json"

def get_last_run_timestamp():
    """Reads the last run timestamp (Unix Timestamp) from the config file."""
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get("last_run", 0)
        except Exception as e:
            print(f"⚠️ Error reading config file: {e}")
    return 0

def update_last_run_timestamp():
    """Updates the config file with the current timestamp."""
    current_ts = int(datetime.now().timestamp())
    with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
        json.dump({"last_run": current_ts}, f, indent=4)
    print("🕒 Config file updated with current timestamp.")

def main():
    print("=" * 60)
    print("[START] STEP 1: Fetching new jobs from scrapers...")
    print("=" * 60)
    
    last_run_ts = get_last_run_timestamp()
    all_jobs = []

    # Fetch jobs using the scraper
    print("\n🔍 Scanning Amdocs...")
    try:
        amdocs_jobs = process_amdocs_jobs(last_run_ts)
        all_jobs.extend(amdocs_jobs)
        print(f"✅ Amdocs: Found {len(amdocs_jobs)} new jobs.")
    except Exception as e:
        print(f"[ERROR] Failed to fetch Amdocs jobs: {e}")

    print("\n🔍 Scanning Microsoft...")
    try:
        msft_jobs = process_microsoft_jobs(last_run_ts)
        all_jobs.extend(msft_jobs)
        print(f"✅ Microsoft: Found {len(msft_jobs)} new jobs.")
    except Exception as e:
        print(f"[ERROR] Failed to fetch Microsoft jobs: {e}")

    update_last_run_timestamp()

    if not all_jobs or (len(all_jobs) == 0):
        print("\n" + "=" * 60)
        print("[RESULT] Step 1 finished: 0 new jobs found across all sources.")
        print("[INFO] Skipping Gemini AI analysis. Process terminated gracefully.")
        print("=" * 60)
        return
        
    print(f"\n[SUCCESS] Step 1 finished. Total jobs fetched: {len(all_jobs)}")
    print("Job Titles Fetched:")
    for j in all_jobs:
        print(f" - {j['title']} (@ {j.get('location', 'Unknown')})")

    print("\n" + "=" * 60)
    print(f"[START] STEP 2: Sending all {len(all_jobs)} jobs to Gemini AI in ONE batch...")
    print("=" * 60)
    
    bot = CareerBotAnalyzer("candidate_config.json")
    analysis_results = bot.analyze_jobs_batch(all_jobs)
    
    if not analysis_results:
        print("\n[ERROR] Step 2 failed: Received empty response from Gemini.")
        return
        
    print("\n[SUCCESS] Step 2 finished. AI Analysis received.")
    print("\n" + "=" * 60)
    print("🎯 FINAL MATCHING RESULTS:")
    print("=" * 60)

    approved_jobs_for_telegram = []

    # Merge results and print
    for result in analysis_results:
        idx = result.get("job_index")
        if idx is not None and idx < len(all_jobs):
            job_data = all_jobs[idx]
            
            print(f"\n📌 Job Title: {job_data['title']}")
            print(f"📍 Location: {job_data['location']}")
            print(f"🔗 Job Link: {job_data['job_link']}")
            print(f"📊 AI Match Score: {result.get('match_score')}%")
            
            should_apply = result.get('should_apply', False)
            print(f"✅ Apply Decision: {'YES' if should_apply else 'NO'}")
            
            if should_apply:
                print(f"📄 Best CV to Send: {result.get('selected_cv_id')}")
            
            approved_jobs_for_telegram.append({
                    "title": job_data['title'],
                    "location": job_data['location'],
                    "score": result.get('match_score'),
                    "cv": result.get('selected_cv_id'),
                    "apply_link": job_data['apply_link']
                })
            
            print(f"💡 AI Reasoning: {result.get('reason')}")
            print("-" * 50)
#send only jobs that are approved by the AI (Apply: YES)
    if approved_jobs_for_telegram:
        print("\n" + "=" * 60)
        print(f"[START] STEP 3: Sending Telegram Notification for {len(approved_jobs_for_telegram)} jobs...")
        print("=" * 60)
        send_telegram_notification(approved_jobs_for_telegram)
    else:
        print("\n[INFO] No jobs met the criteria (Apply: NO). Telegram notification skipped.")

    print("\n[INFO] All processes completed successfully.")

if __name__ == "__main__":
    main()