📲 BioSync - Biometric Attendance Sync Tool for ERPNext
BioSync is a fully customizable ERPNext app that syncs attendance data from external biometric systems into ERPNext’s Employee Checkin doctype — using direct SQL access to biometric databases (MySQL or PostgreSQL).
It is device-agnostic and allows mapping any database schema through an intuitive GUI.

✨ Key Features
🔗 Connect to any biometric database (MySQL or PostgreSQL)

🧩 No vendor lock-in — works with ZKTeco, eSSL, Biotime, etc.

🛠️ GUI-based SQL & field mapping to avoid hardcoding

🔍 Query preview tool with validation before syncing

🚀 Manual and Auto Sync modes (with frequency control)

🧾 Sync log tracking for unmatched or skipped records

📊 Optional Dashboard integration for recent syncs

🧠 How It Works
Define connection to your biometric database from the ERPNext UI

Write your own SELECT query (with :last_sync placeholder)

Map fields like Employee ID, Timestamp, Device ID

Preview data → Test connection → Sync

Auto-sync runs every X minutes if enabled

🛠️ Tech Stack
ERPNext + Frappe Framework

SQLAlchemy for DB abstraction

Python 3.10+

Compatible with Frappe/ERPNext v14+

📦 Installation
bash
Copy
Edit
cd frappe-bench
bench get-app bio_sync
bench --site yoursite install-app bio_sync
