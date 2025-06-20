import frappe
from frappe.utils import now_datetime, add_days

def delete_old_logs():
    dbs = frappe.get_all("Biometric DB Settings", fields=["name", "log_retention_days"])

    for db in dbs:
        retention_days = db.log_retention_days or 30
        cutoff_date = add_days(now_datetime(), -retention_days)

        deleted = frappe.db.delete(
            "Biometric Sync Log",
            {
                "biometric_db": db.name,
                "failed_on": ["<", cutoff_date]
            }
        )

        frappe.logger("bio_sync").info(f"Deleted {deleted} logs older than {retention_days} days for {db.name}")
