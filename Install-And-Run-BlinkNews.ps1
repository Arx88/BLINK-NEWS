<#
.SYNOPSIS
    Installs and runs the BLINK NEWS application.
    This script attempts to install necessary dependencies including Python, Node.js (with npm), and pnpm using winget,
    then sets up the Python virtual environment, installs dependencies, and launches the backend and frontend.
.DESCRIPTION
    Detailed steps:
    1. Checks for winget.
    2. Installs Python via winget if not found.
    3. Installs Node.js LTS (with npm) via winget if not found.
    4. Creates a Python virtual environment (blink_venv).
    5. Installs Python requirements from requirements.txt.
    6. Installs pnpm globally via npm.
    7. Starts the backend Flask server.
    8. Starts the frontend Vite development server.
    Requires PowerShell 5.1 or later.
    May require Administrator privileges for winget installations or to set Execution Policy.
.NOTES
    Author: Jules (AI Assistant)
    Version: 0.1.1
#>

# --- Initial Configuration ---
# Stop on errors
$ErrorActionPreference = 'Stop'

# Attempt to set Execution Policy for the current process to allow script execution
try {
    # Get current execution policy for the process scope
    $currentProcessPolicy = Get-ExecutionPolicy -Scope Process -ErrorAction SilentlyContinue
    if ($currentProcessPolicy -ne "RemoteSigned" -and $currentProcessPolicy -ne "Unrestricted" -and $currentProcessPolicy -ne "Bypass") {
        Write-Host "Attempting to set Execution Policy to 'RemoteSigned' for the current PowerShell process..."
        Write-Host "(This is to ensure the script has permissions to run)"
        Set-ExecutionPolicy RemoteSigned -Scope Process -Force -ErrorAction Stop
        Write-Host "Execution policy for current process set to 'RemoteSigned'."
        Write-Host "This change only affects this current PowerShell session."
    } elseif ($currentProcessPolicy -in ("RemoteSigned", "Unrestricted", "Bypass")) {
        Write-Host "Current process execution policy is already sufficient ($currentProcessPolicy)."
    }
} catch {
    Write-Warning "----------------------------------------------------------------------------------"
    Write-Warning "IMPORTANT: Failed to automatically set the PowerShell Execution Policy for this session."
    Write-Warning "This script might not run correctly if the policy is too restrictive (e.g., 'Restricted')."
    Write-Warning "Current Execution Policy for Process: $(Get-ExecutionPolicy -Scope Process -ErrorAction SilentlyContinue)"
    Write-Warning "Current Execution Policy for User: $(Get-ExecutionPolicy -Scope CurrentUser -ErrorAction SilentlyContinue)"
    Write-Warning "To allow this script to run, you may need to set the policy manually."
    Write-Warning "Open a new PowerShell window AS ADMINISTRATOR and run ONE of the following commands:"
    Write-Warning "  Set-ExecutionPolicy RemoteSigned -Scope CurrentUser  (Recommended for user-specific setting)"
    Write-Warning "  OR"
    Write-Warning "  Set-ExecutionPolicy RemoteSigned -Scope LocalMachine (System-wide, affects all users)"
    Write-Warning "Then, close this window and re-run this script."
    Write-Warning "----------------------------------------------------------------------------------"
    Read-Host -Prompt "Press Enter to exit and then try the steps above"
    exit 1
}

Function Test-Admin {
    $currentUser = New-Object Security.Principal.WindowsPrincipal $(New-Object Security.Principal.WindowsIdentity).GetCurrent()
    $currentUser.IsInRole([Security.Principal.WindowsBuiltinRole]::Administrator)
}

# --- Main Script Logic ---
try {
    Write-Host "Starting BLINK NEWS Setup and Run Script..."
    Write-Host "This script will guide you through installing dependencies and running the application."
    Write-Host "---------------------------------------------------------------------------"

    if (-not (Test-Admin)) {
        Write-Warning "This script may need Administrator privileges to install software using winget."
        Write-Warning "If installations fail, please try running this script as an Administrator."
        # Future: Add logic to self-elevate if desired and possible.
    }

    # --- Check for winget ---
    Write-Host ""
    Write-Host "Step 1: Checking for winget package manager..."
    $wingetPath = Get-Command winget -ErrorAction SilentlyContinue
    if ($null -eq $wingetPath) {
        Write-Warning "----------------------------------------------------------------------------------"
        Write-Warning "ERROR: winget command not found."
        Write-Warning "winget is required to automatically install Python and Node.js."
        Write-Host ""
        Write-Host "How to install winget (it's usually included in modern Windows):"
        Write-Host "1. Open the Microsoft Store."
        Write-Host "2. Search for 'App Installer'."
        Write-Host "3. Install or Update it (Publisher should be 'Microsoft Corporation')."
        Write-Host "After installing/updating App Installer (which includes winget), please re-run this script."
        Write-Warning "----------------------------------------------------------------------------------"
        Read-Host -Prompt "Press Enter to exit script"
        exit 1
    } else {
        Write-Host "winget found: $($wingetPath.Source)"
        try {
            winget --version
        } catch {
            Write-Warning "Could not retrieve winget version, but it seems to be available."
        }
    }
    Write-Host "---------------------------------------------------------------------------"

    # --- Install Python via winget if not found ---
    Write-Host ""
    Write-Host "Step 2: Checking for Python (version 3.9+)..."
    $MinPythonVersion = [version]"3.9"
    $PythonInstalled = $false
    $PythonExePath = Get-Command python -ErrorAction SilentlyContinue

    if ($null -ne $PythonExePath) {
        Write-Host "Python found: $($PythonExePath.Source)"
        try {
            $versionOutput = python --version 2>&1
            Write-Host "Detected Python version: $versionOutput"
            $match = [regex]::Match($versionOutput, "(\d+\.\d+\.\d+)")
            if ($match.Success) {
                $currentPythonVersion = [version]$match.Groups[1].Value
                if ($currentPythonVersion -ge $MinPythonVersion) {
                    Write-Host "Current Python version ($currentPythonVersion) meets the minimum requirement (version $MinPythonVersion or newer)."
                    $PythonInstalled = $true
                } else {
                    Write-Warning "Current Python version ($currentPythonVersion) is older than the required version $MinPythonVersion."
                }
            } else {
                Write-Warning "Could not accurately parse Python version from: $versionOutput"
            }
        } catch {
            Write-Warning "Could not determine Python version. Error: $($_.Exception.Message)"
        }
    } else {
        Write-Host "Python not found in your system's PATH."
    }

    if (-not $PythonInstalled) {
        Write-Host "Attempting to install the latest Python 3 via winget..."
        Write-Host "(This may require Administrator privileges and can take a few minutes)"
        if (-not (Test-Admin)) {
            Write-Warning "Administrator privileges are likely required to install Python using winget."
            Write-Host "If the script fails here, please re-run it as an Administrator."
            # No exit here, let winget try and fail if not admin, error handling below will catch it.
        }
        try {
            Write-Host "Executing: winget install --id Python.Python.3 --exact --accept-source-agreements --accept-package-agreements --scope machine --silent"
            winget install --id Python.Python.3 --exact --accept-source-agreements --accept-package-agreements --scope machine --silent
            Write-Host "Python installation via winget completed."
            Write-Host "Refreshing environment variables to detect new Python installation..."
            $env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")
            $PythonExePath = Get-Command python -ErrorAction SilentlyContinue
            if ($null -ne $PythonExePath) {
                Write-Host "Python successfully installed and found: $($PythonExePath.Source)"
                python --version
                $PythonInstalled = $true
            } else {
                Write-Warning "----------------------------------------------------------------------------------"
                Write-Warning "ERROR: Python was installed by winget, but is still not found in PATH."
                Write-Warning "ACTION REQUIRED: Please RESTART your terminal/PowerShell session and RE-RUN this script."
                Write-Warning "If the issue persists, ensure Python's installation directory is in your system PATH."
                Write-Warning "(e.g., C:\Program Files\Python3x or %LocalAppData%\Programs\Python\Python3x\Scripts\)"
                Write-Warning "----------------------------------------------------------------------------------"
                Read-Host -Prompt "Press Enter to exit script"
                exit 1
            }
        } catch {
            Write-Error "----------------------------------------------------------------------------------"
            Write-Error "ERROR: Failed to install Python via winget."
            Write-Error "Details: $($_.Exception.Message)"
            Write-Host "Please try installing Python (version 3.9 or newer) manually and ensure it's added to your PATH."
            Write-Error "----------------------------------------------------------------------------------"
            Read-Host -Prompt "Press Enter to exit script"
            exit 1
        }
    }
    Write-Host "---------------------------------------------------------------------------"

    # --- Install Node.js (LTS) via winget if not found ---
    Write-Host ""
    Write-Host "Step 3: Checking for Node.js (LTS version) and npm..."
    $NodeInstalled = $false
    $NodeExePath = Get-Command node -ErrorAction SilentlyContinue
    $NpmExePath = Get-Command npm -ErrorAction SilentlyContinue

    if (($null -ne $NodeExePath) -and ($null -ne $NpmExePath)) {
        Write-Host "Node.js found: $($NodeExePath.Source)"
        Write-Host "npm found: $($NpmExePath.Source)"
        try {
            $nodeVersion = node --version
            $npmVersion = npm --version
            Write-Host "Detected Node.js version: $nodeVersion"
            Write-Host "Detected npm version: $npmVersion"
            $NodeInstalled = $true # Assuming any found version is okay for now
        } catch {
             Write-Warning "Could not determine Node.js or npm version. Error: $($_.Exception.Message)"
        }
    } else {
        if ($null -eq $NodeExePath) { Write-Host "Node.js not found in your system's PATH." }
        if ($null -eq $NpmExePath) { Write-Host "npm not found in your system's PATH." }
    }

    if (-not $NodeInstalled) {
        Write-Host "Attempting to install Node.js LTS (includes npm) via winget..."
        Write-Host "(This may require Administrator privileges and can take a few minutes)"
        if (-not (Test-Admin)) {
            Write-Warning "Administrator privileges are likely required to install Node.js using winget."
            Write-Host "If the script fails here, please re-run it as an Administrator."
        }
        try {
            Write-Host "Executing: winget install --id OpenJS.NodeJS.LTS --exact --accept-source-agreements --accept-package-agreements --scope machine --silent"
            winget install --id OpenJS.NodeJS.LTS --exact --accept-source-agreements --accept-package-agreements --scope machine --silent
            Write-Host "Node.js LTS installation via winget completed."
            Write-Host "Refreshing environment variables to detect new Node.js installation..."
            $env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")
            $NodeExePath = Get-Command node -ErrorAction SilentlyContinue
            $NpmExePath = Get-Command npm -ErrorAction SilentlyContinue

            if (($null -ne $NodeExePath) -and ($null -ne $NpmExePath)) {
                Write-Host "Node.js successfully installed and found: $($NodeExePath.Source)"
                Write-Host "npm successfully installed and found: $($NpmExePath.Source)"
                node --version
                npm --version
                $NodeInstalled = $true
            } else {
                Write-Warning "----------------------------------------------------------------------------------"
                Write-Warning "ERROR: Node.js/npm was installed by winget, but is still not found in PATH."
                Write-Warning "ACTION REQUIRED: Please RESTART your terminal/PowerShell session and RE-RUN this script."
                Write-Warning "If the issue persists, ensure Node.js's installation directory is in your system PATH."
                Write-Warning "(e.g., C:\Program Files\nodejs\)"
                Write-Warning "----------------------------------------------------------------------------------"
                Read-Host -Prompt "Press Enter to exit script"
                exit 1
            }
        } catch {
            Write-Error "----------------------------------------------------------------------------------"
            Write-Error "ERROR: Failed to install Node.js LTS via winget."
            Write-Error "Details: $($_.Exception.Message)"
            Write-Host "Please try installing Node.js LTS manually and ensure it and npm are added to your PATH."
            Write-Error "----------------------------------------------------------------------------------"
            Read-Host -Prompt "Press Enter to exit script"
            exit 1
        }
    }
    Write-Host "---------------------------------------------------------------------------"

    # --- Create Python virtual environment and install dependencies ---
    Write-Host ""
    Write-Host "Step 4: Setting up Python virtual environment ('blink_venv')..."
    $VenvDir = "blink_venv"
    $PythonFromVenv = Join-Path -Path $PSScriptRoot -ChildPath (Join-Path $VenvDir "Scripts\python.exe") # Absolute path

    if (-not (Test-Path $PythonFromVenv)) {
        Write-Host "Creating Python virtual environment in '$VenvDir' folder..."
        try {
            $PythonToUseForVenv = if ($null -ne $PythonExePath -and (Test-Path $PythonExePath.Source)) { $PythonExePath.Source } else { "python" }
            Invoke-Expression "$PythonToUseForVenv -m venv (Join-Path -Path $PSScriptRoot -ChildPath $VenvDir)"
            Write-Host "Virtual environment created."
        } catch {
            Write-Error "Failed to create Python virtual environment. Error: $($_.Exception.Message)"
            Read-Host -Prompt "Press Enter to exit script"
            exit 1
        }
    } else {
        Write-Host "Python virtual environment '$VenvDir' already exists."
    }

    Write-Host "Installing Python dependencies from requirements.txt into the virtual environment..."
    Write-Host "(This may take a few moments)"
    $RequirementsFile = Join-Path -Path $PSScriptRoot -ChildPath "requirements.txt"
    if (-not (Test-Path $RequirementsFile)) {
        Write-Error "ERROR: requirements.txt not found at $RequirementsFile!"
        Read-Host -Prompt "Press Enter to exit script"
        exit 1
    }
    try {
        Invoke-Expression "$PythonFromVenv -m pip install --upgrade pip"
        Invoke-Expression "$PythonFromVenv -m pip install -r '$RequirementsFile'"
        Write-Host "Python dependencies installed successfully."
    } catch {
        Write-Error "Failed to install Python dependencies. Error: $($_.Exception.Message)"
        Read-Host -Prompt "Press Enter to exit script"
        exit 1
    }
    Write-Host "---------------------------------------------------------------------------"

    # --- Install pnpm globally via npm ---
    Write-Host ""
    Write-Host "Step 5: Checking for pnpm (Node.js package manager)..."
    $PnpmInstalled = $false
    $PnpmExePath = Get-Command pnpm -ErrorAction SilentlyContinue

    if ($null -ne $PnpmExePath) {
        Write-Host "pnpm found: $($PnpmExePath.Source)"
        try {
            $pnpmVersion = pnpm --version
            Write-Host "Detected pnpm version: $pnpmVersion"
            $PnpmInstalled = $true
        } catch {
            Write-Warning "Could not determine pnpm version. Error: $($_.Exception.Message)"
            $PnpmInstalled = $true # pnpm command exists, so assume it's usable
        }
    } else {
        Write-Host "pnpm not found in your system's PATH."
    }

    if (-not $PnpmInstalled) {
        Write-Host "Attempting to install pnpm globally via npm..."
        Write-Host "(This may take a few moments)"
        try {
            Invoke-Expression "npm install -g pnpm"
            Write-Host "pnpm global installation command executed."
            Write-Host "Refreshing environment variables to detect new pnpm installation..."
            $env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User") + ";" + [System.Environment]::GetEnvironmentVariable("Path","Process")
            $PnpmExePath = Get-Command pnpm -ErrorAction SilentlyContinue
            if ($null -ne $PnpmExePath) {
                Write-Host "pnpm successfully installed and found: $($PnpmExePath.Source)"
                pnpm --version
                $PnpmInstalled = $true
            } else {
                Write-Warning "----------------------------------------------------------------------------------"
                Write-Warning "WARNING: pnpm was installed by npm, but is still not found in PATH."
                Write-Warning "ACTION REQUIRED: Please RESTART your terminal/PowerShell session and RE-RUN this script."
                Write-Warning "If the issue persists, ensure npm's global bin directory is in your system PATH."
                Write-Warning "(You can find this directory by running 'npm config get prefix' in a new terminal)"
                Write-Warning "----------------------------------------------------------------------------------"
                # Not exiting, as the application startup part has its own pnpm check.
            }
        } catch {
            Write-Error "----------------------------------------------------------------------------------"
            Write-Error "ERROR: Failed to install pnpm globally via npm."
            Write-Error "Details: $($_.Exception.Message)"
            Write-Host "Please try installing pnpm manually by running: npm install -g pnpm"
            Write-Error "----------------------------------------------------------------------------------"
        }
    }
    Write-Host "---------------------------------------------------------------------------"

    # --- Start Backend and Frontend Applications ---
    Write-Host ""
    Write-Host "Step 6: Starting Blink News application (Backend and Frontend)..."

    $PythonForApp = $PythonFromVenv # Use Python from venv
    $BackendScriptToRun = Join-Path -Path $PSScriptRoot -ChildPath "news-blink-backend\src\app.py"
    $FrontendDirToRun = Join-Path -Path $PSScriptRoot -ChildPath "news-blink-frontend"

    if (-not (Test-Path $BackendScriptToRun)) {
        Write-Error "ERROR: Backend script not found at $BackendScriptToRun. Cannot start backend."
        Read-Host -Prompt "Press Enter to exit script"
        exit 1
    }
    if (-not (Test-Path $FrontendDirToRun)) {
        Write-Error "ERROR: Frontend directory not found at $FrontendDirToRun. Cannot start frontend."
        Read-Host -Prompt "Press Enter to exit script"
        exit 1
    }

    $PnpmForApp = Get-Command pnpm -ErrorAction SilentlyContinue
    if ($null -eq $PnpmForApp) {
        Write-Error "----------------------------------------------------------------------------------"
        Write-Error "ERROR: pnpm command not found. Cannot start the frontend."
        Write-Warning "This script attempted to install pnpm. If the installation seemed successful,"
        Write-Warning "you might need to RESTART PowerShell or your computer for pnpm to be recognized in PATH."
        Write-Warning "Alternatively, try running 'npm install -g pnpm' manually in a new Administrator terminal,"
        Write-Warning "then RE-RUN this script."
        Write-Error "----------------------------------------------------------------------------------"
        Read-Host -Prompt "Press Enter to exit script"
        exit 1
    }

    Write-Host "Starting Backend (Flask server)..."
    Write-Host "(A new PowerShell window will open for the backend)"
    try {
        Start-Process powershell -ArgumentList "-NoExit", "-Command", "& '$PythonForApp' '$BackendScriptToRun'" -WindowStyle Normal
        Write-Host "Backend process launch command issued."
        Write-Host "Look for a new window. Backend typically runs on http://127.0.0.1:5000"
    } catch {
        Write-Error "Failed to start Backend. Error: $($_.Exception.Message)"
    }

    Write-Host "Starting Frontend (Vite dev server)..."
    Write-Host "(A new PowerShell window will open for the frontend. This may take a minute to compile.)"
    try {
        Start-Process powershell -ArgumentList "-NoExit", "-Command", "& $($PnpmForApp.Source) --prefix '$FrontendDirToRun' run dev" -WindowStyle Normal
        Write-Host "Frontend process launch command issued."
        Write-Host "Look for a new window. Frontend typically runs on http://localhost:5173"
    } catch {
        Write-Error "Failed to start Frontend. Error: $($_.Exception.Message)"
    }

    Write-Host "BLINK NEWS Setup and Run Script finished its tasks."

} catch {
    Write-Error "----------------------------------------------------------------------------------"
    Write-Error "AN UNEXPECTED ERROR OCCURRED:"
    Write-Error "$($_.Exception.Message)"
    Write-Error "Script execution halted."
    Write-Error "----------------------------------------------------------------------------------"
    if ($Host.Name -eq "ConsoleHost") {
        Read-Host -Prompt "Press Enter to exit"
    }
    exit 1
}

Write-Host ""
Write-Host "---------------------------------------------------------------------------"
Write-Host "SCRIPT COMPLETE - WHAT TO DO NEXT:"
Write-Host "---------------------------------------------------------------------------"
Write-Host "1. TWO NEW PowerShell windows should have opened:"
Write-Host "   - One for the BACKEND (Flask server)."
Write-Host "   - One for the FRONTEND (Vite development server)."
Write-Host ""
Write-Host "2. Check the FRONTEND window:"
Write-Host "   - Wait for it to compile. When ready, it will show a 'Local:' URL."
Write-Host "   - It typically looks like: http://localhost:5173"
Write-Host "   - Open this URL in your web browser to see BLINK NEWS."
Write-Host ""
Write-Host "3. Check the BACKEND window:"
Write-Host "   - It should show messages indicating it's running, typically on port 5000."
Write-Host "   - You usually don't interact with this window directly, but keep it open."
Write-Host ""
Write-Host "4. TO STOP THE APPLICATION:"
Write-Host "   - Go to EACH of the two new PowerShell windows."
Write-Host "   - Press CTRL+C in each window."
Write-Host "   - You may need to confirm by typing 'Y' or 'N' and then Enter."
Write-Host "---------------------------------------------------------------------------"

if ($Host.Name -eq "ConsoleHost") {
    Read-Host -Prompt "All automated tasks are done. Press Enter to close this main script window."
}
