from scrapers.amdox import process_new_jobs
from analyzer import CareerBotAnalyzer
from notifier import send_telegram_notification

def main():
    print("=" * 60)
    print("[START] STEP 1: Fetching new jobs from scrapers...")
    print("=" * 60)
    
    # Fetch jobs using the scraper
    try:
        jobs = process_new_jobs()
    except Exception as e:
        print(f"[ERROR] Failed to fetch jobs: {e}")
        return

    # Check if we got 0 jobs
    if not jobs or len(jobs) == 0:
        print("\n[RESULT] Step 1 finished: 0 new jobs found.")
        print("[INFO] Skipping Gemini AI analysis. Process terminated gracefully.")
        return
        
    print(f"\n[SUCCESS] Step 1 finished. Total jobs fetched: {len(jobs)}")
    print("Job Titles Fetched:")
    for j in jobs:
        print(f" - {j['title']}")

    print("\n" + "=" * 60)
    print(f"[START] STEP 2: Sending all {len(jobs)} jobs to Gemini AI in ONE batch...")
    print("=" * 60)
    
    bot = CareerBotAnalyzer("candidate_config.json")
    analysis_results = bot.analyze_jobs_batch(jobs)
    
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
        if idx is not None and idx < len(jobs):
            job_data = jobs[idx]
            
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