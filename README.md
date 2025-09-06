# Enterprise-web-development-Projectplan

📊 MoMo SMS Data Dashboard
Members & Responsibilities

Glo – Frontend & Documentation

README.md (setup, run instructions, project overview)

index.html (dashboard entry)

web/styles.css (dashboard styling)

web/assets/ (images/icons)

User-facing documentation

Kenny – ETL (Data Flow & Processing)

etl/config.py (paths, thresholds, categories)

etl/parse_xml.py (parse XML)

etl/clean_normalize.py (normalize data)

etl/categorize.py (categorize transactions)

Contribute to etl/run.py

Tifare – Database & API

data/db.sqlite3 (SQLite database)

etl/load_db.py (load parsed data to DB)

api/ (FastAPI for transactions/analytics)

Connect backend → frontend with dashboard.json

Frank – Project Lead & Integration

.env.example (env vars for DB URL/path)

requirements.txt (dependencies)

data/ (raw, processed, logs, dead_letter)

etl/run.py (pipeline orchestration)

scripts/ (automate ETL/export/serve)

tests/ (unit testing coordination)

📌 Project Overview

This project is an enterprise-level fullstack application designed to process MoMo SMS transaction data in XML format.

The pipeline works as follows:

Extract & Parse – XML transactions are parsed.

Clean & Normalize – Transaction amounts, phone numbers, and dates are standardized.

Categorize – Transactions grouped into categories (e.g., deposits, withdrawals, transfers).

Load – Data stored in an SQLite database.

Visualize – Frontend dashboard displays analytics (charts, tables).

⚙️ Setup Instructions
1. Clone the repository
git clone https://github.com/tifarekaseke/Enterprise-web-development-Projectplan.git

cd Enterpise-web-development-Projectplan

2. Install dependencies
pip install -r requirements.txt

3. Setup environment variables

Copy .env.example → .env and update:

DATABASE_URL=sqlite:///data/db.sqlite3

4. Run ETL pipeline
python etl/run.py --xml data/raw/momo.xml

5. Export JSON for frontend
bash scripts/export_json.sh

6. Serve frontend
python -m http.server 8000


Go to: http://localhost:8000

🗂️ Project Structure
.
├── README.md
├── .env.example
├── requirements.txt
├── index.html
├── web/
│   ├── styles.css
│   ├── chart_handler.js
│   └── assets/
├── data/
│   ├── raw/
│   ├── processed/
│   ├── db.sqlite3
│   └── logs/
├── etl/
│   ├── config.py
│   ├── parse_xml.py
│   ├── clean_normalize.py
│   ├── categorize.py
│   ├── load_db.py
│   └── run.py
├── api/
│   ├── app.py
│   ├── db.py
│   └── schemas.py
├── scripts/
└── tests/

🖼️ System Architecture

Diagram (Draw.io/Miro):
https://lucid.app/lucidchart/790473e5-3b45-4606-b15a-df609d0c7bb8/edit?invitationId=inv_e04eb2d6-476b-4a1c-bcd7-c635c86b404b&page=0_0#

📅 Scrum Board

Our Jira board (To Do, In Progress, Done):
👉 [https://alustudent-team-gms7kuss.atlassian.net/jira/software/projects/KAN/boards/1?atlOrigin=eyJpIjoiYjc1ODVlOTMxMzhjNDhiNmFkNDk0N2RhZDU3NmRlZGMiLCJwIjoiaiJ9]

