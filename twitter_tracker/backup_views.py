from django.http import FileResponse, JsonResponse
from django.core.management import call_command
import os

def backup_database(request):
    """ Generate and serve an SQLite database backup """
    backup_path = "db_backup.json"  # Name of the backup file
    try:
        # Create a JSON backup
        with open(backup_path, "w", encoding="utf-8") as f:
            call_command("dumpdata", stdout=f)

        # Serve the file for download
        return FileResponse(open(backup_path, "rb"), as_attachment=True, filename="db_backup.json")

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
