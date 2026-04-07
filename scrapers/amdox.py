import requests
import urllib3
import time
import random
from bs4 import BeautifulSoup
import sys

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def fetch_and_filter_initial_jobs(last_run_ts):
    """
    Fetches the initial job list from the API and filters out jobs
    posted before the last run.
    """
    api_url = f"https://jobs.amdocs.com/api/pcsx/search?domain=amdocs.com&query=&location=&start=0&sort_by=timestamp&filter_job_location=israel-+raanana+%28amdocs+site%29&filter_job_location=israel-+shderot+%28amdocs+site%29"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        "Accept": "application/json"
    }
    
    print(f"🚀 Querying API. Filtering old jobs from {last_run_ts}...")
    
    try:
        response = requests.get(api_url, headers=headers, verify=False, timeout=10)
        response.raise_for_status()
        json_data = response.json()
        
        if not json_data or "data" not in json_data or "positions" not in json_data["data"]:
            return []
            
        all_positions = json_data["data"]["positions"]
        
        new_positions = [pos for pos in all_positions if pos.get("postedTs", 0) > last_run_ts]
        return new_positions
        
    except Exception as e:
        print(f"❌ Error fetching data from API: {e}")
        return []

def fetch_job_description(position_id):
    """
    Calls the specific job details API using the position_id,
    filters out generic marketing texts, and returns a clean description.
    """
    api_url = f"https://jobs.amdocs.com/api/pcsx/position_details?position_id={position_id}&domain=amdocs.com&hl=en"
    
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
            
            for tag in soup.find_all(lambda t: t.name in ['h2', 'h3', 'b', 'strong'] and 'who are we' in t.get_text(strip=True).lower()):
                wrapper = tag.find_parent('div', style=lambda s: s and 'padding' in s.lower())
                if wrapper:
                    wrapper.decompose()
                    
            for tag in soup.find_all(lambda t: 'equal opportunity employer' in t.get_text().lower()):
                parent_p = tag.find_parent(['p', 'div'])
                if parent_p:
                    parent_p.decompose()

            raw_text = soup.get_text(separator='\n', strip=True)
            
            clean_text = "\n".join([line for line in raw_text.split('\n') if line.strip()])
            
            return clean_text
        else:
            return "Description not available."
            
    except Exception as e:
        print(f"❌ Error fetching description from API: {e}")
        return "Error fetching details."

def process_amdocs_jobs(last_run_ts):
    """
    Manages the overall workflow: fetch, filter, deep-dive into details,
    and return an organized list.
    """
    new_positions = fetch_and_filter_initial_jobs(last_run_ts)
    
    if new_positions is None or (not new_positions and "Error" in str(sys.exc_info())):
        print("⚠️ Skipping timestamp update due to fetch error.")
        return []
    
    if not new_positions:
        print("📭 No new jobs found since the last scan.")
        return []
        
    print(f"✅ Found {len(new_positions)} new jobs. Extracting full descriptions...\n")
    
    base_domain = "https://jobs.amdocs.com"
    detailed_jobs = []
    
    for index, pos in enumerate(new_positions, 1):
        title = pos.get("name", "Untitled")
        locations = " / ".join(pos.get("locations", []))
        
        position_url = pos.get("positionUrl", "")
        position_id = position_url.rstrip('/').split('/')[-1]
        
        job_link = base_domain + position_url
        apply_link = f"https://jobs.amdocs.com/careers/apply?pid={position_id}"
        
        print(f"  [{index}/{len(new_positions)}] Fetching details for: {title}...")
        description = fetch_job_description(position_id)
        
        detailed_jobs.append({
            "title": title,
            "location": locations,
            "job_link": job_link,
            "apply_link": apply_link,
            "description": description
        })
        
        time.sleep(random.uniform(1.5, 3.0))
    return detailed_jobs

if __name__ == "__main__":
    final_jobs_list = process_amdocs_jobs(1772323200)
    
    if final_jobs_list:
        print("\n" + "="*50)
        print("🎯 Full Jobs Summary:")
        for job in final_jobs_list:
            print(f"\n📌 Title: {job['title']}")
            print(f"📍 Location: {job['location']}")
            print(f"🔗 Job Link: {job['job_link']}")
            print(f"🚀 Apply Link: {job['apply_link']}")
            print(f"📄 Description (Partial):\n{job['description'][:300]}...\n")
            print("-" * 50)