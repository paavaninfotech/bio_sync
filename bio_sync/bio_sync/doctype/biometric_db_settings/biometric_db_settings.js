// Copyright (c) 2025, Paavan Infotech and contributors
// For license information, please see license.txt

// frappe.ui.form.on("Biometric DB Setting", {
// 	refresh(frm) {

// 	},
// });
frappe.ui.form.on('Biometric DB Settings', {
    refresh: function(frm) {
        // Existing buttons...
        frm.add_custom_button('✅ Test Connection', function () {
            frappe.call({
                method: "bio_sync.sync.fetch.test_db_connection",
                args: { name: frm.doc.name },
                callback: function (r) {
                    if (r.message === "Success") {
                        frappe.msgprint(__('✅ Connection Successful'));
                    } else {
                        frappe.msgprint({ title: __('❌ Connection Failed'), indicator: 'red', message: r.message });
                    }
                }
            });
        });

        frm.add_custom_button('🔍 Preview Query & Mapping', function () {
            frappe.call({
                method: "bio_sync.sync.preview.preview_sql_query_with_mapping",
                args: { name: frm.doc.name },
                callback: function (r) {
                    if (r.message && r.message.data && r.message.columns) {
                        let preview_data = r.message.data;
                        let columns = r.message.columns;

                        let html = `
                            <div style="overflow-x: auto;">
                                <table class="table table-bordered table-sm">
                                    <thead><tr>
                                        ${columns.map(c => `<th>${c}</th>`).join("")}
                                    </tr></thead>
                                    <tbody>
                                        ${preview_data.map(row => `
                                            <tr>
                                                ${columns.map(c => `<td>${frappe.utils.escape_html(String(row[c] ?? ""))}</td>`).join("")}
                                            </tr>`).join("")}
                                    </tbody>
                                </table>
                            </div>
                        `;

                        frappe.msgprint({
                            title: __("SQL Output Preview"),
                            message: html,
                            indicator: "blue",
                            wide: true
                        });
                    } else {
                        frappe.msgprint({
                            title: __("Error"),
                            indicator: "red",
                            message: r.message
                        });
                    }
                }
            });
        });

        // ✅ NEW: Sync Now Button
        frm.add_custom_button('🚀 Sync Now', function () {
            frappe.call({
                method: "bio_sync.sync.fetch.sync_now",
                args: { name: frm.doc.name },
                callback: function (r) {
                    frappe.msgprint({
                        title: __("Sync Result"),
                        message: r.message,
                        indicator: "green"
                    });
                    frm.reload_doc();
                }
            });
        });
    }
});
