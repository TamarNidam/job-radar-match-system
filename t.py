import requests

url = "https://careers.checkpoint.com/index.php"

# עדכון הפרמטרים כדי שיפנו לעמוד של משרה ספציפית
params = {
    "m": "cpcareers",         # מודול המשרות
    "a": "show",              # הפעולה היא כעת 'show' (הצגה) במקום 'search'
    "joborderid": "25168",    # מזהה המשרה הספציפית
    "source": ""              # פרמטר ריק שהיה בקישור המקורי
}

# הוספת כותרות (Headers) כדי שהשרת יחשוב שאנחנו דפדפן אמיתי
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}

# שליחת הבקשה
response = requests.get(url, params=params, headers=headers)

# הדפסת קוד ה-HTML שחוזר (ממנו תוכל לחלץ את תיאור המשרה)
print(response.text)