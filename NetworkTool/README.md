# Network Interface Manager (Windows 11)

Yes — this app can be packaged as a **single `.exe`** so users do **not** need to install Python.

## About admin rights
Short answer: you cannot permanently avoid elevation for this use case.

Changing adapter IPv4 settings (`netsh interface ip set ...`) requires elevated privileges on Windows. What you *can* do is package the app so it automatically asks for elevation (UAC prompt) when launched, instead of expecting users to manually right-click "Run as administrator".

This repo now supports that flow:
- The app auto-relaunches itself with elevation if needed.
- The packaged `.exe` includes a UAC admin manifest.

## What this tool does
This tool provides a simple, non-technical UI for selecting a network adapter and switching between:
- **DHCP (automatic IP/DNS)**
- **Static IPv4 configuration**

It is designed for environments where users cannot change IP settings from the modern Settings app and must use legacy adapter workflows.

## Features
- Lists available network interfaces.
- Lets user choose one interface from a table.
- Applies DHCP settings quickly.
- Applies static IP/subnet/gateway and optional DNS.
- Includes shortcut button to open `Control Panel > Network Connections` (`ncpa.cpl`).
- Automatically prompts for admin rights when required.

## Runtime requirements (for users)
- Windows 11
- **No Python install required** when using the packaged `.exe`
- User must be allowed by policy/UAC to run elevated app sessions

## Install (for end users)
1. Download `NetworkInterfaceManager.exe` from your internal software share (or from IT).
2. Create a folder such as `C:\Program Files\Network Interface Manager\`.
3. Copy `NetworkInterfaceManager.exe` into that folder.
4. (Optional) Right-click the `.exe` and choose **Send to > Desktop (create shortcut)**.
5. Launch the app from the shortcut or `.exe`. Approve the Windows UAC prompt.

> If your organization blocks writes to `Program Files`, install to a user folder like
> `C:\Users\<username>\Apps\NetworkInterfaceManager\` instead.

## Install (for IT deployment)
- Build the executable using the steps below.
- Optionally code-sign `NetworkInterfaceManager.exe`.
- Distribute through your endpoint management tool (Intune, SCCM, PDQ, etc.) or software share.
- Create a Start Menu/Desktop shortcut for users as part of deployment.

## Run from source (developer mode)
```powershell
cd NetworkTool
python network_interface_manager.py
```

## Build a single `.exe` (recommended)
From PowerShell in this folder:
```powershell
cd NetworkTool
powershell -ExecutionPolicy Bypass -File .\build_exe.ps1
```

Output file:
- `dist\NetworkInterfaceManager.exe`

## Manual build commands (alternative)
```powershell
cd NetworkTool
python -m pip install --upgrade pyinstaller
python -m PyInstaller --noconfirm --clean --onefile --windowed --uac-admin --name NetworkInterfaceManager network_interface_manager.py
```

## Distribution notes
- You can share only `NetworkInterfaceManager.exe` from the `dist` folder.
- On launch, Windows will show a UAC prompt (expected by design).
- Some security tools may flag newly created unsigned executables. If needed, code-sign the `.exe` internally.
- Group policy / permissions can still block IP changes.

## Notes
- This tool uses `netsh` commands under the hood.
- If your organization enforces policy restrictions, some interfaces/settings may still be blocked.
