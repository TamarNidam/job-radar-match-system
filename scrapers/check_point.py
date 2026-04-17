import requests
import urllib3
import time
import random
from bs4 import BeautifulSoup

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def fetch_and_filter_initial_jobs(recent_job_ids):
    """
    Fetches job listings with specified filters, paginates until it encounters 
    any of the job IDs provided in the recent_job_ids list.
    """
    api_url = "https://careers.checkpoint.com/index.php"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    
    new_positions = []
    start = 0
    found_known_job = False
    
    print(f"🚀 Scanning Check Point Careers...")
    print(f"🔍 Searching for new jobs until we hit any of these recent IDs: {recent_job_ids}\n")
    
    while not found_known_job:
        params = {
            "module": "cpcareers",
            "a": "search",
            "fa[]": [
                "department_s:Security & Risk Management",
                "department_s:R&D",
                "department_s:Product Management",
                "department_s:IT & System Administration",
                "department_s:Data and Analytics",
                "country_ss:Israel",
                "seniority_s:Experienced",
                "seniority_s:Entry Level"
            ],
            "sort": "date_published_display_s desc",
            "start": start 
        }
        
        try:
            response = requests.get(api_url, params=params, headers=headers, verify=False, timeout=15)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            job_cards = soup.find_all('div', class_='position')
            
            if not job_cards:
                print("⚠️ No more jobs found on this page. Reached the end of the list.")
                break
                
            for card in job_cards:
                title_tag = None
                for a_tag in card.find_all('a'):
                    if 'joborderid=' in a_tag.get('href', ''):
                        title_tag = a_tag
                        break
                
                if not title_tag:
                    continue
                    
                title = title_tag.text.strip()
                link = title_tag['href']
                
                if link.startswith('index.php'):
                    link = f"https://careers.checkpoint.com/{link}"
                    
                job_id = 0
                if 'joborderid=' in link:
                    try:
                        job_id = int(link.split('joborderid=')[-1].split('&')[0])
                    except ValueError:
                        pass
                
                if job_id in recent_job_ids:
                    print(f"🛑 Reached a known job (ID: {job_id}). Stopping page traversal.")
                    found_known_job = True
                    break 
                
                location = "Unknown Location"
                pos_info = card.find('div', class_='posInfo')
                if pos_info:
                    loc_tag = pos_info.find('img', class_='place')
                    if loc_tag and loc_tag.parent:
                        location = loc_tag.parent.text.strip()

                new_positions.append({
                    "id": job_id,
                    "title": title,
                    "location": location,
                    "job_link": link
                })
                
            start += 10
            
        except Exception as e:
            print(f"❌ Error fetching data from search page: {e}")
            break

    return new_positions

def fetch_job_description(job_link): 
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Referer": "https://careers.checkpoint.com/index.php?m=cpcareers&a=search"
    }
    
    try:
        response = requests.get(job_link, headers=headers, verify=False, timeout=15)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        container = soup.find('div', id='jobOrderInfo')

        if container:
            return container.get_text(separator='\n', strip=True)
        else:
            print("Description container not found.")
            return ""
            
    except Exception as e:
        print(f"❌ Error fetching description: {e}")
        return "Error fetching details."
    

def process_checkpoint_jobs(recent_job_ids):
    """
    Main engine: Collects the job list, then extracts details for each new job.
    """

    new_positions = fetch_and_filter_initial_jobs(recent_job_ids)
    
    if not new_positions:
        print("📭 No new jobs found since the last scan.")
        return []
        
    print(f"\n✅ Found {len(new_positions)} new jobs! Extracting full descriptions...\n")
    
    detailed_jobs = []
    
    for index, job in enumerate(new_positions, 1):
        delay_seconds = random.uniform(20.0, 45.0)
        print(f"⏳ Waiting {delay_seconds:.1f} seconds to prevent blocking...")
        time.sleep(delay_seconds)
        
        print(f"  [{index}/{len(new_positions)}] Fetching details for: {job['title']} (ID: {job['id']})...")
        print(f"     Link: {job['job_link']}")
        
        description = fetch_job_description(job['job_link'])
        
        detailed_jobs.append({
            "id": job['id'],
            "title": job['title'],
            "location": job['location'],
            "job_link": job['job_link'],
            "description": description
        })
        
    return detailed_jobs

if __name__ == "__main__":
    RECENT_JOB_IDS = [25430, 25425, 25420] 
    
    final_jobs_list = process_checkpoint_jobs(RECENT_JOB_IDS)
    
    if final_jobs_list:
        print("\n" + "="*50)
        print("🎯 Jobs Summary:")
        for job in final_jobs_list:
            print(f"\n📌 Title: {job['title']} (ID: {job['id']})")
            print(f"📍 Location: {job['location']}")
            print(f"🔗 Link: {job['job_link']}")
            print(f"📄 Description (Partial):\n{job['description'][:2500]}...\n")
            print("-" * 50)