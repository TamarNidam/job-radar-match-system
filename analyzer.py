import json
import google.generativeai as genai
import pypdf
import os
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

class CareerBotAnalyzer:
    def __init__(self, config_path="candidate_config.json"):
        with open(config_path, 'r', encoding='utf-8') as f:
            self.config = json.load(f)
        
        genai.configure(api_key=GEMINI_API_KEY)
        self.model = genai.GenerativeModel('gemini-2.5-flash')
        self.settings = self.config['candidate']['settings']

    def _extract_text_from_pdf(self, file_name):        
        try:
            cv_folder = self.config['candidate']['cv_folder']
        except (KeyError, AttributeError):
            print("❌ Error: Config structure invalid or missing cv_folder")
            return ""

        base_dir = os.path.dirname(os.path.abspath(__file__))
        full_path = os.path.normpath(os.path.join(base_dir, cv_folder, file_name))
        
        if not os.path.exists(full_path):
            print(f"❌ Error: File {file_name} not found at {full_path}.")
            return ""

        try:
            reader = pypdf.PdfReader(full_path)
            text = ""
            for page in reader.pages:
                content = page.extract_text()
                if content:
                    text += content
            
            if not text.strip():
                print(f"⚠️ Warning: File {file_name} is empty (scanned image?)")
                
            return text[:2500] 
            
        except Exception as e:
            print(f"❌ Unexpected error reading {file_name}: {e}")
            return ""

    def _prepare_cv_context(self):
        cv_context = ""
        for cv in self.config['candidate']['cv_directory']:
            content = self._extract_text_from_pdf(cv['file'])
            cv_context += f"\n--- CV_ID: {cv['id']} ---\nFocus: {cv['focus']}\nContent Summary: {content}\n"
        return cv_context


# work. old
    def analyze_job(self, job_title, job_description):
        cv_context = self._prepare_cv_context()
        cand = self.config['candidate']

        prompt = f"""
        Role: Strategic Tech Headhunter.
        Candidate: {cand['name']}. Level: {cand['experience']['seniority_level']}.
        
        EVALUATION LOGIC:
        - Tamar has intense, high-load experience since 2024, performing at a Senior level.
        - Treat her {cand['experience']['actual_years']} years as equivalent to 5 years in standard environments due to complexity (Clearance: {cand['experience']['has_clearance']}).
        - Strictly reject if location is in {cand['location']['blacklist']}.
        
        JOB TO ANALYZE: {job_title}
        DESCRIPTION: {job_description}
        
        AVAILABLE RESUMES:
        {cv_context}
        
        TASK:
        Ignore purely chronological filters if technical match is > 90%. Pick the best CV.
        
        STRICT FILTERS:
        - Actual Experience: {cand['experience']['actual_years']} years.
        - Max Allowed Gap: {self.settings['max_experience_gap']} years.
        - Location Blacklist: {cand['location']['blacklist']}.
        - Role Blacklist: {cand['roles']['blacklist_keywords']}.
        
        JOB DETAILS:
        Title: {job_title}
        Description: {job_description}
        
        AVAILABLE CV VARIANTS:
        {cv_context}
        
        OUTPUT RULES:
        1. Evaluate if job meets hard filters.
        2. Select the CV ID that best matches the job's technical stack.
        3. Provide a match_score (0-100).
        
        RETURN JSON ONLY:
        {{
            "match_score": int,
            "should_apply": bool (if match_score >= {self.settings['min_apply_score']}),
            "selected_cv_id": "string",
            "reason": "concise explanation"
        }}
        """

        try:
            response = self.model.generate_content(
                prompt, 
                generation_config={"response_mime_type": "application/json"}
            )
            return json.loads(response.text)
        except Exception as e:
            return {"error": str(e), "should_apply": False}

# new
    def analyze_jobs_batch(self, jobs_list):
        """
        Takes a list of job dictionaries, sends them ALL in ONE prompt to Gemini,
        and returns a list of evaluated JSON responses.
        """
        if not jobs_list:
            return []

        cv_context = self._prepare_cv_context()
        cand = self.config['candidate']

        # Prepare the combined text for all jobs
        jobs_text = ""
        for idx, job in enumerate(jobs_list):
            # Truncating description slightly to save tokens if it's too long
            desc = job['description'][:1500] + "..." if len(job['description']) > 1500 else job['description']
            jobs_text += f"\n[JOB_INDEX: {idx}]\nTitle: {job['title']}\nLocation: {job['location']}\nDescription: {desc}\n"

        prompt = f"""
        Role: Strategic Tech Headhunter.
        Candidate: {cand['name']}. Level: {cand['experience']['seniority_level']}.
        
        EVALUATION LOGIC:
        - Treat her {cand['experience']['actual_years']} years as equivalent to 5 years in standard environments due to complexity (Clearance: {cand['experience']['has_clearance']}).
        - Strictly reject if location is in {cand['location']['blacklist']}.
        - Ignore purely chronological filters if technical match is > 90%. Pick the best CV.
        
        STRICT FILTERS:
        - Actual Experience: {cand['experience']['actual_years']} years.
        - Max Allowed Gap: {self.settings['max_experience_gap']} years.
        - Location Blacklist: {cand['location']['blacklist']}.
        - Role Blacklist: {cand['roles']['blacklist_keywords']}.
        
        AVAILABLE RESUMES:
        {cv_context}
        
        TASK:
        Evaluate the following list of jobs. For each job, check if it meets the hard filters.
        Select the CV ID that best matches the job's technical stack. Provide a match_score (0-100).
        
        JOBS TO ANALYZE:
        {jobs_text}
        
        OUTPUT RULES:
        RETURN ONLY A VALID JSON ARRAY. No markdown wrapping, no extra text.
        Structure:
        [
            {{
                "job_index": int (matching the index provided),
                "match_score": int,
                "should_apply": bool (if match_score >= {self.settings['min_apply_score']}),
                "selected_cv_id": "string",
                "reason": "concise explanation"
            }}
        ]
        """

        try:
            response = self.model.generate_content(
                prompt, 
                generation_config={"response_mime_type": "application/json"}
            )
            
            # Clean possible markdown formatting (```json ... ```)
            raw_text = response.text.strip()
            if raw_text.startswith("```json"):
                raw_text = raw_text[7:]
            if raw_text.endswith("```"):
                raw_text = raw_text[:-3]
                
            return json.loads(raw_text)
            
        except Exception as e:
            print(f"❌ Error connecting to Gemini API: {e}")
            return []