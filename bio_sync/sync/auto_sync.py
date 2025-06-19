import frappe
from frappe.utils import now_datetime, get_datetime, time_diff
from .fetch import sync_now

@frappe.whitelist()
def run_scheduled_sync():
    dbs = frappe.get_all("Biometric DB Settings", filters={"auto_sync_enabled": 1}, fields=["name", "sync_frequency", "last_sync_time"])

    for db in dbs:
        try:
            last_sync = db.last_sync_time or "2000-01-01 00:00:00"
            diff = time_diff(now_datetime(), get_datetime(last_sync)).total_seconds() / 60

            freq = int(db.sync_frequency or 10)

            if diff >= freq:
                frappe.logger("bio_sync").info(f"Auto syncing {db.name}")
                sync_now(db.name)

        except Exception as e:
            frappe.log_error(f"Auto Sync Error: {str(e)}", title=f"Biometric Auto Sync - {db.name}")
