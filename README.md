# 🚀 JobPilot (AI CareerBot)

JobPilot is an automated, AI-driven job scraping and matching system. It continuously monitors target career pages, extracts job descriptions, and uses Google's Gemini AI to evaluate the technical fit against candidate CVs. Highly matched roles are automatically sent as notifications via Telegram.

The project is fully automated using GitHub Actions, ensuring a hands-off, continuous pipeline for job hunting.

## ✨ Features

* **Automated Scraping:** Fetches newly posted jobs while safely ignoring previously processed ones using a timestamp state file.
* **Smart AI Evaluation:** Integrates with `google-generativeai` (Gemini 2.5 Flash) to parse complex job descriptions and evaluate them against strict candidate requirements (seniority, tech stack, location blacklists, and clearance).
* **Dynamic CV Routing:** Parses local PDF resumes using `pypdf` and dynamically selects the best-tailored CV variant for each specific job.
* **Instant Notifications:** Sends beautifully formatted alerts directly to a Telegram chat, including match scores and direct application links.
* **CI/CD Automation:** Runs entirely in the cloud via GitHub Actions on a scheduled cron job (every 5 hours).

## 🏗️ Project Structure

```text
JobPilot/
├── scrapers/
│   └── amdox.py            # API scraper and HTML parser for Amdocs careers
├── analyzer.py             # Gemini AI integration and CV PDF parsing logic
├── notifier.py             # Telegram bot notification system
├── main.py                 # Main orchestrator script
├── requirements.txt        # Python dependencies
├── lastRun_config.json     # State management for the scraper's last run timestamp
├── candidate_config.json   # Candidate details, hard filters, and CV metadata
└── .github/workflows/
    └── jobpilot.yml        # GitHub Actions CI/CD configuration
```

## ⚙️ Setup & Installation

### 1. Local Environment
Clone the repository and install the required dependencies:
```bash
pip install -r requirements.txt
```

### 2. Configuration Files
Ensure you have the following configuration files in your root directory:

* `candidate_config.json`: Contains your personal profile, tech stack, hard filters (e.g., max experience gap, location blacklists), and references to your PDF CVs.
* `lastRun_config.json`: Initializes the scraper timestamp. (e.g., `{"last_run": 0}`)

### 3. Environment Variables
For local testing, set the following environment variables. **Do not hardcode these in your scripts:**

* `GEMINI_API_KEY`: Your Google Gemini API Key.
* `TELEGRAM_TOKEN`: Your Telegram Bot Token.
* `TELEGRAM_CHAT_ID`: Your target Telegram Chat ID.

## 🤖 Automation (GitHub Actions)
This repository is configured to run automatically without a dedicated server.
The `.github/workflows/jobpilot.yml` file sets up an Ubuntu runner, installs dependencies, securely injects API keys from **GitHub Secrets**, runs the pipeline, and commits the updated `lastRun_config.json` back to the repository to maintain state.

**To deploy securely:**
1. Go to your GitHub Repository **Settings** > **Secrets and variables** > **Actions**.
2. Add `GEMINI_API_KEY`, `TELEGRAM_TOKEN`, and `TELEGRAM_CHAT_ID` as Repository Secrets.

## 🛠️ Technologies Used
* **Python 3.10**
* **Google Generative AI** (Gemini 2.5 Flash)
* **BeautifulSoup4** (HTML Parsing)
* **PyPDF** (Resume parsing)
* **GitHub Actions** (Automation)
* **Telegram Bot API**