import requests
import urllib3
import time
import random
from bs4 import BeautifulSoup

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def fetch_and_filter_initial_jobs(last_seen_job_id):
    """
    מושך את המשרות עם הפילטרים המבוקשים, ממשיך לדפדף עד שפוגש את המשרה האחרונה שראינו.
    """
    api_url = "https://careers.checkpoint.com/index.php"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    
    new_positions = []
    start = 0
    found_last_job = False
    
    print(f"🚀 סורק את Check Point...")
    print(f"🔍 מחפש משרות חדשות עד שנגיע ל-ID: {last_seen_job_id}\n")
    
    while not found_last_job:
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
                print("⚠️ לא נמצאו עוד משרות בעמוד זה. ייתכן שהגענו לסוף הרשימה.")
                break
                
            for card in job_cards:
                title_tag = None
                for a_tag in card.find_all('a'):
                    if 'joborderid=' in a_tag.get('href', ''):
                        title_tag = a_tag
                        print(f"🔎 נמצא כותרת עם joborderid: {a_tag.text.strip()}")
                        break
                
                if not title_tag:
                    print("⚠️ לא נמצא כותרת עם joborderid. דילוג על כרטיס זה.") 
                    continue
                    
                title = title_tag.text.strip()
                link = title_tag['href']
                
                # תיקון הקישור לפורמט מלא
                if link.startswith('index.php'):
                    link = f"https://careers.checkpoint.com/{link}"
                    print(f"🔗 מתקן קישור: {link}")
                    
                # חילוץ ה-ID של המשרה (joborderid) מתוך הקישור
                job_id = 0
                if 'joborderid=' in link:
                    try:
                        job_id = int(link.split('joborderid=')[-1].split('&')[0])
                        print(f"📌 מחלץ joborderid: {job_id}")
                    except ValueError:
                        print(f"⚠️ לא ניתן לחלץ joborderid מתוך הקישור: {link}")
                        pass
                
                # תנאי העצירה החכם: הגענו למשרה האחרונה שאנחנו מכירים!
                if job_id == last_seen_job_id:
                    print(f"🛑 הגענו למשרה מוכרת (ID: {job_id}). עוצר את איסוף הרשימה.")
                    found_last_job = True
                    break # יוצא מלולאת ה-for
                
                # חילוץ המיקום
                location = "Unknown Location"
                pos_info = card.find('div', class_='posInfo')
                if pos_info:
                    loc_tag = pos_info.find('img', class_='place')
                    if loc_tag and loc_tag.parent:
                        location = loc_tag.parent.text.strip()

                # מוסיפים את המשרה החדשה לרשימה
                new_positions.append({
                    "id": job_id,
                    "title": title,
                    "location": location,
                    "job_link": link
                })
                
            # עוברים לעמוד הבא (קפיצה של 10 תוצאות)
            start += 10
            
        except Exception as e:
            print(f"❌ Error fetching data from search page: {e}")
            break

    return new_positions

def fetch_job_description(job_link):
    """
    נכנס לקישור של המשרה הספציפית ומחלץ את התוכן המלא שלה מתוך jobOrderInfo.
    """
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    
    try:
        response = requests.get(job_link, headers=headers, verify=False, timeout=15)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # חיפוש הקונטיינר המרכזי שמכיל את כל תיאור המשרה בעמוד המלא
        description_container = soup.find('div', id='jobOrderInfo')
        
        if description_container:
            # מנקה את ה-HTML ומחזיר את כל הטקסט (דרישות, אחריות וכו') עם ירידות שורה
            return description_container.get_text(separator='\n', strip=True)
        else:
            return "Description container not found."
            
    except Exception as e:
        print(f"❌ Error fetching description: {e}")
        return "Error fetching details."
    

def process_checkpoint_jobs(last_seen_job_id):
    """
    המנוע הראשי: אוסף את הרשימה, ואז שואב את הפרטים מכל עמוד.
    """
    new_positions = fetch_and_filter_initial_jobs(last_seen_job_id)
    
    if not new_positions:
        print("📭 לא נמצאו משרות חדשות מאז הסריקה האחרונה.")
        return []
        
    print(f"\n✅ נמצאו {len(new_positions)} משרות חדשות! מתחיל לחלץ את התוכן מכל אחת...\n")
    
    detailed_jobs = []
    
    for index, job in enumerate(new_positions, 1):
        print(f"  [{index}/{len(new_positions)}] שואב מידע עבור: {job['title']} (ID: {job['id']})...")
        print(f"     קישור: {job['job_link']}")
        description = fetch_job_description(job['job_link'])
        
        detailed_jobs.append({
            "id": job['id'],
            "title": job['title'],
            "location": job['location'],
            "job_link": job['job_link'],
            "description": description
        })
        
        # השהייה חכמה למניעת חסימה
        time.sleep(random.uniform(1.0, 2.5))
        
    return detailed_jobs

if __name__ == "__main__":
    LAST_JOB_ID = 25430 
    
    final_jobs_list = process_checkpoint_jobs(LAST_JOB_ID)
    
    if final_jobs_list:
        print("\n" + "="*50)
        print("🎯 סיכום משרות:")
        for job in final_jobs_list:
            print(f"\n📌 כותרת: {job['title']} (ID: {job['id']})")
            print(f"📍 מיקום: {job['location']}")
            print(f"🔗 קישור: {job['job_link']}")
            print(f"📄 תיאור (חלקי):\n{job['description'][:2500]}...\n")
            print("-" * 50)
        