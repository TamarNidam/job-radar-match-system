import json
from analyzer import CareerBotAnalyzer

def run_test_suite():
    # אתחול האנלייזר (יוודא שקובץ ה-config קיים באותה תיקייה)
    try:
        bot = CareerBotAnalyzer("candidate_config.json")
    except FileNotFoundError:
        print("Error: candidate_config.json not found! Fix it first.")
        return

    test_cases = [
        {
            "id": "CASE_1_GIS_PERFECT",
            "title": "Senior Backend & GIS Engineer",
            "desc": "We need a C# expert specializing in spatial data, coordinate systems, and .NET Core. Location: Beer Sheva (South). 4 years experience required."
        },
        {
            "id": "CASE_2_MANAGEMENT_STRETCH",
            "title": "VP R&D / Group Manager",
            "desc": "Looking for a leader with 10+ years of experience to manage 50 developers. High-level strategy and budget management. Location: Tel Aviv."
        },
        {
            "id": "CASE_3_LOCATION_FAIL",
            "title": "Full Stack Developer",
            "desc": "Great opportunity in Haifa (North). Requires React and Node.js. 100% on-site."
        }
    ]

    print(f"{'='*20} STARTING BOT TEST {'='*20}\n")

    for case in test_cases:
        print(f"Testing Case: {case['id']} - {case['title']}")
        result = bot.analyze_job(case['title'], case['desc'])
        
        # הדפסה קריאה של התוצאות
        print(f"Match Score: {result.get('match_score')}")
        print(f"Apply Decision: {'✅ YES' if result.get('should_apply') else '❌ NO'}")
        print(f"Selected CV: {result.get('selected_cv_id')}")
        print(f"Reason: {result.get('reason')}")
        print("-" * 50)

if __name__ == "__main__":
    run_test_suite()