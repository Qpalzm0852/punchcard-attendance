# PunchCard Attendance

A Windows desktop prototype for face-assisted attendance. An operator can enroll a user, verify a face for check-in or check-out, and review the resulting records locally.

## Architecture

```mermaid
flowchart LR
    UI["wxPython desktop UI"] --> Camera["OpenCV webcam capture"]
    Camera --> Detect["Haar face detection"]
    Detect --> Crop["In-memory JPEG crop"]
    Crop --> Cloud["Baidu face detection and identity search"]
    UI --> Cloud
    Cloud --> Local["SQLite attendance records"]
    Local --> UI
```

wxPython supplies the desktop UI. OpenCV detects face regions in a camera frame. The Baidu Face service evaluates the crop and matches it against the configured face group. The desktop application records attendance in SQLite. The application also exposes enrollment, deletion and an attendance grid.

## Local setup

Use Windows with Python 3.11 and an available webcam. From the repository root in PowerShell:

```powershell
py -3.11 -m venv .venv
& .\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

Set the three environment variables listed in `.env.example` in your own shell using your credentials and a dedicated test face group. Then run:

```powershell
& .\.venv\Scripts\python.exe punchcard.py
```

For a demo, use a dedicated group with authorized test participants and synthetic employee records. The captured JPEG crop is held in memory and sent to the configured face service. The local SQLite file is created at runtime and contains names and attendance timestamps. Keep that file local.

## Scope

This repository contains the application entry point and a configuration template. The OpenCV wheel provides the Haar cascade. The classroom scripts, photos, original database and course archive are excluded. The application implements a single attendance record per user and retains the original prototype's fixed late-arrival threshold.


## Verification

An offline test run with a mocked face service and an in-memory SQLite database covered environment-based configuration, JPEG payload encoding, successful enrollment and check-in, and the failed-enrollment path. Live camera and Baidu API interoperability require a separate local run.
