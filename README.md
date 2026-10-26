Duplicate File Cleaner and Log Automation

Project Overview

Duplicate File Cleaner and Log Automation is a Python-based automation project that identifies duplicate files using MD5 checksums. It helps users find duplicate files, remove unwanted copies with confirmation, generate log reports, and schedule repeated scans.

Features

- Detects duplicate files using MD5 checksum.
- Groups files with identical content.
- Asks for confirmation before deleting duplicate files.
- Generates timestamped log reports.
- Supports scheduled scanning.
- Supports sending log reports through email when email settings are configured.

Technologies Used

- Python
- hashlib
- os
- datetime
- schedule
- smtplib
- EmailMessage

Project Structure

Duplicate_File_cleaner_And_Log_Automation/
├── DuplicateFileCleaner.py
├── Test_Folder/
├── logs/
├── README.md
├── requirements.txt
└── .gitignore

Installation

1. Install Python 3 on your system.
2. Open the project folder in VS Code.
3. Open the terminal.
4. Install the required package:

pip install schedule

How to Run

Run the Python file with the test folder path:

python DuplicateFileCleaner.py "Test_Folder"

Choose "once" to run a single scan or "schedule" to enable repeated scans, as prompted by the program.

How It Works

1. The program scans the specified folder.
2. It calculates the MD5 checksum of each file.
3. Files with matching checksums are identified as duplicates.
4. The user confirms whether duplicate copies should be deleted.
5. A log report records the scan results.
6. Scheduled scans and email reports can be used when configured.

Safety Note

Always test the program using sample files before scanning important folders. Review the files carefully before confirming deletion.

Author

Yash Chavan