import frappe
from sqlalchemy import create_engine, text

@frappe.whitelist()
def preview_sql_query_with_mapping(name):
    doc = frappe.get_doc("Biometric DB Settings", name)

    try:
        if not doc.sql_query:
            return "SQL query is empty."

        if doc.db_type == "MySQL":
            url = f"mysql+pymysql://{doc.db_user}:{doc.get_password('db_password')}@{doc.db_host}:{doc.db_port}/{doc.db_name}"
        else:
            url = f"postgresql://{doc.db_user}:{doc.get_password('db_password')}@{doc.db_host}:{doc.db_port}/{doc.db_name}"

        engine = create_engine(url)

        with engine.connect() as conn:
            result = conn.execute(text(doc.sql_query))
            rows = result.mappings().fetchmany(10)
            rows = [dict(row) for row in rows]  # guaranteed dict list



        if not rows:
            return "Query executed but returned no data."

        sample = rows[0]
        missing = []

        for field_name, label in [
            (doc.user_id_field, "USER ID"),
            (doc.check_time_field, "CHECK TIME"),
            (doc.log_type_field, "LOG TYPE"),
            (doc.device_id_field, "DEVICE ID"),
        ]:
            if field_name and field_name not in sample:
                missing.append(f"{label} → '{field_name}' not found in query output.")

        if missing:
            frappe.msgprint({
                title: "⚠️ Mapping Warnings",
                message: "<br>".join(missing),
                indicator: "orange"
            })

        return {
            "columns": list(sample.keys()),
            "data": rows
        }

    except Exception as e:
        return f"❌ Error: {str(e)}"
