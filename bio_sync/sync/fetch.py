import frappe
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
from frappe.utils import now_datetime

@frappe.whitelist()
def test_db_connection(name):
    doc = frappe.get_doc("Biometric DB Settings", name)

    try:
        if doc.db_type == "MySQL":
            url = f"mysql+pymysql://{doc.db_user}:{doc.get_password('db_password')}@{doc.db_host}:{doc.db_port}/{doc.db_name}"
        else:
            url = f"postgresql://{doc.db_user}:{doc.get_password('db_password')}@{doc.db_host}:{doc.db_port}/{doc.db_name}"

        engine = create_engine(url)
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))  # ✅ Wrap with text()
        return "Success"
    except SQLAlchemyError as e:
        return str(e)

@frappe.whitelist()
def sync_now(name):
    doc = frappe.get_doc("Biometric DB Settings", name)
    last_sync = doc.last_sync_time or "2000-01-01 00:00:00"

    if not doc.sql_query:
        frappe.throw("SQL Query is empty in Biometric DB Settings.")

    # Append WHERE clause if not already present
    user_sql = doc.sql_query.strip()
    if "where" not in user_sql.lower():
        frappe.throw("Please include a WHERE clause in your SQL query to filter by time.")

    if doc.db_type == "MySQL":
        url = f"mysql+pymysql://{doc.db_user}:{doc.get_password('db_password')}@{doc.db_host}:{doc.db_port}/{doc.db_name}"
    else:
        url = f"postgresql://{doc.db_user}:{doc.get_password('db_password')}@{doc.db_host}:{doc.db_port}/{doc.db_name}"

    engine = create_engine(url)
    inserted, skipped = 0, 0

    with engine.connect() as conn:
        result = conn.execute(text(user_sql), {"last_sync": last_sync}).mappings().fetchall()
        rows = [dict(row) for row in result]

        for row in rows:
            emp_id = str(row.get(doc.user_id_field))
            check_time = row.get(doc.check_time_field)
            log_type = row.get(doc.log_type_field) if doc.log_type_field else "IN"
            device_id = row.get(doc.device_id_field) if doc.device_id_field else "Biometric"

            if not emp_id or not check_time:
                log_sync_failure(doc.name, "Missing employee ID or check time", row)
                continue

            employee = frappe.db.get_value("Employee", { "attendance_device_id": emp_id })
            if not employee:
                log_sync_failure(doc.name, f"No employee found for attendance_device_id: {emp_id}", row)
                skipped += 1
                continue

            # Avoid duplicate entries
            if not frappe.db.exists("Employee Checkin", {"employee": employee, "time": check_time}):
                frappe.get_doc({
                    "doctype": "Employee Checkin",
                    "employee": employee,
                    "time": check_time,
                    "log_type": log_type,
                    "device_id": device_id
                }).insert(ignore_permissions=True)
                inserted += 1
            else:
                skipped += 1

    doc.last_sync_time = now_datetime()
    doc.save(ignore_permissions=True)

    return f"✅ Sync complete: {inserted} inserted, {skipped} skipped."

def log_sync_failure(biometric_db_name, reason, row):
    frappe.get_doc({
        "doctype": "Biometric Sync Log",
        "biometric_db": biometric_db_name,
        "failed_on": now_datetime(),
        "reason": reason,
        "row_json": frappe.as_json(row)
    }).insert(ignore_permissions=True)
