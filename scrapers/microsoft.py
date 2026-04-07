import requests
import urllib3
import json
import time
import random
from bs4 import BeautifulSoup
from datetime import datetime, timedelta

# ביטול אזהרות SSL
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# קובץ קונפיגורציה נפרד למייקרוסופט כדי לא לדרוס את אמדוקס
CONFIG_FILE = "lastRun_config_msft.json"

def get_last_run_timestamp():
    """Reads the last run timestamp or returns 7 days ago as default."""
    return 1772323200

def update_last_run_timestamp():
    """Updates the config file with the current timestamp."""
    current_ts = int(datetime.now().timestamp())
    with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
        json.dump({"last_run": current_ts}, f, indent=4)
    print("🕒 Microsoft config file updated.")

def fetch_and_filter_initial_jobs():
    """
    Fetches jobs from Microsoft's Phenom API for Israel.
    """
    # ה-URL המלא שסיפקת עם כל הפילטרים הרלוונטיים
    api_url = "https://apply.careers.microsoft.com/api/pcsx/search?domain=microsoft.com&query=&location=israel&start=0&sort_by=timestamp&filter_include_remote=1&filter_employment_type=full-time&filter_profession=software+engineering&filter_profession=product+management&filter_profession=security+engineering&filter_profession=design+%26+creative&filter_profession=administration&filter_profession=analytics"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        "Accept": "application/json"
    }
    
    last_run = get_last_run_timestamp()
    last_run_date = datetime.fromtimestamp(last_run).strftime('%Y-%m-%d %H:%M:%S')
    print(f"🚀 Querying Microsoft API. Filtering jobs older than {last_run_date}...")
    
    try:
        response = requests.get(api_url, headers=headers, verify=False, timeout=10)
        response.raise_for_status()
        json_data = response.json()
        
        if not json_data or "data" not in json_data or "positions" not in json_data["data"]:
            return []
            
        all_positions = json_data["data"]["positions"]
        
        # סינון לפי Timestamp
        new_positions = [pos for pos in all_positions if pos.get("postedTs", 0) > last_run]
        return new_positions
        
    except Exception as e:
        print(f"❌ Error fetching data from Microsoft API: {e}")
        return []

def fetch_job_description(position_id):
    """
    Fetches the full job description from Microsoft's details API.
    """
    api_url = f"https://apply.careers.microsoft.com/api/pcsx/position_details?position_id={position_id}&domain=microsoft.com&hl=en"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        "Accept": "application/json"
    }
    
    try:
        response = requests.get(api_url, headers=headers, verify=False, timeout=15)
        response.raise_for_status()
        json_data = response.json()
        
        description_html = json_data.get("data", {}).get("jobDescription", "")
        
        if description_html:
            soup = BeautifulSoup(description_html, 'html.parser')
            
            # ניקוי טקסטים גנריים של מייקרוסופט (דומה ללוגיקה שלך)
            for tag in soup.find_all(lambda t: t.name in ['h2', 'h3', 'b', 'strong'] and 'who we are' in t.get_text(strip=True).lower()):
                wrapper = tag.find_parent('div')
                if wrapper: wrapper.decompose()

            raw_text = soup.get_text(separator='\n', strip=True)
            clean_text = "\n".join([line for line in raw_text.split('\n') if line.strip()])
            return clean_text
        else:
            return "Description not available."
            
    except Exception as e:
        print(f"❌ Error fetching description for {position_id}: {e}")
        return "Error fetching details."

def process_microsoft_jobs():
    """
    Main workflow for Microsoft scraper.
    """
    new_positions = fetch_and_filter_initial_jobs()
    
    if not new_positions:
        print("📭 No new Microsoft jobs found since the last scan.")
        # update_last_run_timestamp()
        return []
        
    print(f"✅ Found {len(new_positions)} new jobs at Microsoft. Extracting full descriptions...\n")
    
    base_domain = "https://apply.careers.microsoft.com"
    detailed_jobs = []
    
    for index, pos in enumerate(new_positions, 1):
        title = pos.get("name", "Untitled")
        locations = " / ".join(pos.get("locations", []))
        
        # המזהה הייחודי של המשרה
        position_id = pos.get("id")
        position_url = pos.get("positionUrl", "")
        
        # בניית לינקים
        job_link = base_domain + position_url
        apply_link = f"https://apply.careers.microsoft.com/careers?pid={position_id}"
        
        print(f"  [{index}/{len(new_positions)}] Fetching details for: {title}...")
        description = fetch_job_description(position_id)
        
        detailed_jobs.append({
            "title": title,
            "location": locations,
            "job_link": job_link,
            "apply_link": apply_link,
            "description": description
        })
        
        # שינה קלה למניעת חסימות
        time.sleep(random.uniform(1, 2.5))
        
    update_last_run_timestamp()
    return detailed_jobs

if __name__ == "__main__":
    final_jobs_list = process_microsoft_jobs()
    
    if final_jobs_list:
        print("\n" + "="*50)
        print("🎯 Microsoft Jobs Summary:")
        for job in final_jobs_list:
            print(f"\n📌 Title: {job['title']}")
            print(f"📍 Location: {job['location']}")
            print(f"🔗 Link: {job['job_link']}")
            print(f"📄 Description (Partial):\n{job['description'][:300]}...\n")
            print("-" * 50)