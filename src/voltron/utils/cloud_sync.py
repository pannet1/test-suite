import requests
import os
import json

def upload_report(file_path, api_endpoint, api_key=None):
    """
    Uploads a JSON diagnostic report to a remote cloud server.
    """
    if not os.path.exists(file_path):
        return {"success": False, "error": f"File {file_path} not found."}

    try:
        with open(file_path, 'r') as f:
            data = json.load(f)

        headers = {'Content-Type': 'application/json'}
        if api_key:
            headers['Authorization'] = f'Bearer {api_key}'

        response = requests.post(api_endpoint, json=data, headers=headers, timeout=10)
        
        if response.status_code == 200 or response.status_code == 201:
            return {"success": True, "server_response": response.json()}
        else:
            return {"success": False, "error": f"Server returned {response.status_code}: {response.text}"}

    except Exception as e:
        return {"success": False, "error": str(e)}

def sync_pending_reports(reports_dir, api_endpoint, api_key=None):
    """
    Iterates through the reports directory and uploads any files 
    that haven't been synced yet (could implement a .synced tracking).
    """
    results = []
    for filename in os.listdir(reports_dir):
        if filename.endswith(".json") and not filename.endswith(".synced.json"):
            file_path = os.path.join(reports_dir, filename)
            print(f"Syncing {filename}...")
            res = upload_report(file_path, api_endpoint, api_key)
            if res["success"]:
                # Mark as synced by renaming
                os.rename(file_path, file_path + ".synced")
            results.append({filename: res})
    return results
