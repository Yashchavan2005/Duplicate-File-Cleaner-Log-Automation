# ============================================================
# Project Name : Duplicate File Cleaner & Log Automation
# Author Name  : Yash Chavan
# Date         : 26 October 2026
# Language     : Python
# Description  : Detect duplicate files using MD5, delete extra
#                copies after confirmation, generate log reports,
#                schedule scans and email reports automatically.
# ============================================================

import os
import hashlib
import time
import datetime
import schedule
import smtplib
import sys

from email.message import EmailMessage


# -------------------- EMAIL CONFIGURATION --------------------

# Set these environment variables before enabling email:
# EMAIL_SENDER, EMAIL_PASSWORD, EMAIL_RECEIVER

EMAIL_SENDER = os.getenv("EMAIL_SENDER")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
EMAIL_RECEIVER = os.getenv("EMAIL_RECEIVER")


# -------------------- STEP 1: CALCULATE CHECKSUM --------------------

def CalculateChecksum(FileName):
    """Calculate the MD5 checksum of a file."""

    hobj = hashlib.md5()

    # Open file in binary mode and read in small chunks
    with open(FileName, "rb") as fobj:
        while True:
            Buffer = fobj.read(1024)

            if not Buffer:
                break

            hobj.update(Buffer)

    # Return hexadecimal checksum
    return hobj.hexdigest()


# -------------------- STEP 2: FIND DUPLICATE FILES --------------------

def FindDuplicate(DirectoryName):
    """Find files with matching checksums."""

    if not os.path.isdir(DirectoryName):
        print("Invalid directory:", DirectoryName)
        return None

    Duplicate = {}

    # Scan the directory and its subdirectories
    for FolderName, SubFolder, FileNames in os.walk(DirectoryName):
        for fname in FileNames:
            FilePath = os.path.join(FolderName, fname)

            try:
                Checksum = CalculateChecksum(FilePath)

                # Group files by checksum
                if Checksum in Duplicate:
                    Duplicate[Checksum].append(FilePath)
                else:
                    Duplicate[Checksum] = [FilePath]

            except OSError as e:
                print("Unable to read:", FilePath, e)

    return Duplicate


# -------------------- STEP 3: SEND LOG BY EMAIL --------------------

def SendEmail(LogFile):
    """Send the generated log file as an email attachment."""

    # Check whether email configuration is available
    if not all([EMAIL_SENDER, EMAIL_PASSWORD, EMAIL_RECEIVER]):
        print("Email not configured. Log saved locally.")
        return

    try:
        # Create email message
        msg = EmailMessage()
        msg["Subject"] = "Duplicate File Cleaner - Log Report"
        msg["From"] = EMAIL_SENDER
        msg["To"] = EMAIL_RECEIVER

        msg.set_content(
            "Hello,\n\n"
            "Please find the Duplicate File Cleaner log report attached.\n\n"
            "Regards,\nYash Chavan"
        )

        # Read the log file for attachment
        with open(LogFile, "rb") as fobj:
            FileData = fobj.read()

        msg.add_attachment(
            FileData,
            maintype="text",
            subtype="plain",
            filename=os.path.basename(LogFile)
        )

        # Connect securely to Gmail SMTP
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(EMAIL_SENDER, EMAIL_PASSWORD)
            server.send_message(msg)

        print("Log emailed successfully.")

    except Exception as e:
        print("Email sending failed:", e)
        print("Log file is still saved locally:", LogFile)


# -------------------- STEP 4: SCAN, DELETE AND LOG --------------------

def DeleteDuplicate(DirectoryName):
    """Find duplicates, optionally delete them, and create a log."""

    StartTime = time.time()

    MyDict = FindDuplicate(DirectoryName)

    if MyDict is None:
        return

    # Keep groups with more than one file
    Result = [
        files for files in MyDict.values()
        if len(files) > 1
    ]

    TotalFiles = sum(len(files) for files in MyDict.values())
    TotalDeleted = 0

    # Create timestamped log filename
    CurrentTime = datetime.datetime.now()

    LogFile = (
        "DuplicateLog_"
        + CurrentTime.strftime("%d_%m_%Y_%H_%M_%S")
        + ".txt"
    )

    # Ask for confirmation only when duplicates are found
    Confirm = "no"

    if Result:
        print("\nDuplicate Files Found:")

        for files in Result:
            print("\nDuplicate Group:")

            for path in files:
                print(path)

        Confirm = input(
            "\nDelete duplicate files? (yes/no): "
        ).strip().lower()

    else:
        print("No duplicate files found.")

    # Delete extra copies only after confirmation
    DeleteAllowed = Confirm == "yes"

    with open(LogFile, "w", encoding="utf-8") as fobj:

        fobj.write("=========================================\n")
        fobj.write("      DUPLICATE FILE REPORT\n")
        fobj.write("=========================================\n\n")

        fobj.write("Author : Yash Chavan\n")
        fobj.write("Project Date : 26-10-2026\n")

        fobj.write(
            "Scan Date : "
            + CurrentTime.strftime("%d-%m-%Y")
            + "\n"
        )

        fobj.write(
            "Scan Time : "
            + CurrentTime.strftime("%H:%M:%S")
            + "\n"
        )

        fobj.write("Directory : " + DirectoryName + "\n")

        fobj.write(
            "Total Files Scanned : "
            + str(TotalFiles)
            + "\n"
        )

        fobj.write(
            "Duplicate Groups Found : "
            + str(len(Result))
            + "\n\n"
        )

        # Record each duplicate group
        for files in Result:

            fobj.write("\nDuplicate Group:\n")
            fobj.write("Kept: " + files[0] + "\n")

            if DeleteAllowed:

                for path in files[1:]:

                    try:
                        os.remove(path)
                        TotalDeleted += 1

                        fobj.write("Deleted: " + path + "\n")

                    except OSError as e:

                        fobj.write(
                            "ERROR deleting "
                            + path
                            + ": "
                            + str(e)
                            + "\n"
                        )

            else:

                for path in files[1:]:
                    fobj.write("Not deleted: " + path + "\n")

        # Calculate total execution time
        RequiredTime = time.time() - StartTime

        fobj.write("\n-----------------------------------------\n")

        fobj.write(
            "Total Duplicate Files Deleted : "
            + str(TotalDeleted)
            + "\n"
        )

        fobj.write(
            "Total Time Required : "
            + str(round(RequiredTime, 3))
            + " Seconds\n"
        )

        fobj.write("-----------------------------------------\n")

    # Display final summary
    print("\n========== SUMMARY ==========")
    print("Total Files Scanned :", TotalFiles)
    print("Duplicate Groups :", len(Result))
    print("Total Deleted Files :", TotalDeleted)
    print("Log File Created :", LogFile)

    # Email the log report
    SendEmail(LogFile)


# -------------------- STEP 5: SCHEDULE AUTOMATIC SCANS --------------------

def ScheduledScan(DirectoryName):
    """Run a scan automatically at the scheduled interval."""

    print("\nScheduled scan started...")
    DeleteDuplicate(DirectoryName)


# -------------------- STEP 6: PROGRAM ENTRY POINT --------------------

def main():
    """Start one scan or schedule repeated scans."""

    if len(sys.argv) != 2:

        print(
            "Usage: python DuplicateFileCleaner.py DirectoryName"
        )

        return

    DirectoryName = sys.argv[1]

    # Ask whether the user wants a scheduled scan
    Choice = input(
        "Run once or schedule scans? (once/schedule): "
    ).strip().lower()

    if Choice == "once":

        DeleteDuplicate(DirectoryName)

    elif Choice == "schedule":

        try:
            Minutes = int(
                input("Run scan every how many minutes? ")
            )

            if Minutes < 1:
                print("Interval must be at least 1 minute.")
                return

            # Schedule recurring scans
            schedule.every(Minutes).minutes.do(
                ScheduledScan, DirectoryName
            )

            print(
                f"Automatic scan scheduled every {Minutes} minute(s)."
            )

            print("Keep this program running to continue scheduling.")
            print("Press Ctrl+C to stop.")

            # Keep checking for scheduled tasks
            try:

                while True:
                    schedule.run_pending()
                    time.sleep(1)

            except KeyboardInterrupt:
                print("\nScheduling stopped.")

        except ValueError:
            print("Please enter a valid number of minutes.")

    else:
        print("Invalid choice. Enter once or schedule.")


if __name__ == "__main__":
    main()

# ======================== END OF PROJECT ==========================
