import frappe
import json


from frappe.utils import now



@frappe.whitelist(allow_guest=True)
def last_data_sync():
    try:
        if frappe.local.request.method != "POST":
            return {
                'status_code': 405,
                'message': 'Only POST requests are allowed'
            }

        # Extract form data
        form_data = frappe.form_dict
        current_datetime = now()
        last_sync = current_datetime
        os_version = form_data.get("os_version")
        hardware_version = form_data.get("hardware_version")

        if not (last_sync and os_version and hardware_version):
            return {
                'status_code': 400,
                'message': 'Incomplete data. Please provide last_sync, os_version, and hardware_version.'
            }

        # Convert os_version to JSON string
        os_version_str = json.dumps(os_version)
        urrent_datetime = now()

        # Create a new document
        new_data = frappe.get_doc({
            "doctype": "POS Terminal",
            "last_sync": current_datetime,
            "os_version": os_version_str,  # Insert the JSON string
            "hardware_version": hardware_version
        })

        # Insert or save the document
        try:
            new_data.insert(ignore_permissions=True)
            frappe.db.commit()
            return {
                'status_code': 200,
                'message': 'Data synced successfully'
            }
        except Exception as e:
            error_message = f"Error inserting data: {str(e)}"
            frappe.log_error(error_message)
            frappe.db.rollback()
            return {
                'status_code': 500,
                'message': f'Error inserting data. Rollback performed. {error_message}'
            }

    except Exception as e:
        error_message = f"Error in last_data_sync: {str(e)}"
        frappe.log_error(error_message)
        return {
            'status_code': 500,
            'message': f'Internal Server Error: {error_message}'
        }




@frappe.whitelist(allow_guest=True)
def sync_data_compare(current_datetime):
    
    last_data_sync = frappe.db.sql(""" select sync_datetime,force_update,data from `tabSync Register` where sync_datetime > '{0}' """.format(current_datetime))
    return last_data_sync
