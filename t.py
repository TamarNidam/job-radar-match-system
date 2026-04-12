import requests
from bs4 import BeautifulSoup


headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}
    
try:
    response = requests.get("https://careers.checkpoint.com/index.php?m=cpcareers&a=show&joborderid=25457&source=", headers=headers, verify=False, timeout=15)
    response.raise_for_status()
        
    soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find the main container holding the job description
    description_container = soup.find('div', id='jobOrderInfo')
        
    if description_container:
        print(description_container.text.strip())
    else:
        print("Description container not found.")
            
except Exception as e:
        print(f"❌ Error fetching description: {e}")
