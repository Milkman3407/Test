param(
    [string]$PythonExe = "python",
    [switch]$Clean
)

$ErrorActionPreference = "Stop"

if ($Clean) {
    Remove-Item -Recurse -Force build, dist -ErrorAction SilentlyContinue
    Remove-Item -Force network_interface_manager.spec -ErrorAction SilentlyContinue
}

Write-Host "Installing/upgrading PyInstaller..."
& $PythonExe -m pip install --upgrade pyinstaller

Write-Host "Building executable (UAC admin manifest enabled)..."
& $PythonExe -m PyInstaller --noconfirm --clean --onefile --windowed --uac-admin --name NetworkInterfaceManager network_interface_manager.py

Write-Host "Done. Executable located at: $(Join-Path (Get-Location) 'dist\NetworkInterfaceManager.exe')"
