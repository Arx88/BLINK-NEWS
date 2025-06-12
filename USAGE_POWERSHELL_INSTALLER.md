# Using the Blink News PowerShell Installer (`Install-And-Run-BlinkNews.ps1`)

This script automates the setup and execution of the BLINK NEWS application on a Windows environment. It attempts to install necessary dependencies like Python and Node.js (via `winget`), sets up the project, and then launches the backend and frontend servers.

## Prerequisites

1.  **Windows Operating System:** Windows 10 (version 1709 or later) or Windows 11 is recommended for `winget` compatibility.
2.  **PowerShell:** PowerShell 5.1 or later (usually included with Windows).
3.  **Administrator Privileges:** You will likely need to run the script as an Administrator for it to install software using `winget`. The script will prompt if it detects it's not running with admin rights when needed.
4.  **Internet Connection:** Required to download dependencies (`winget` packages, Python packages, npm packages).
5.  **Microsoft Store Access (Potentially):** If `winget` itself (via "App Installer") is not on your system, the script will guide you to install it from the Microsoft Store.

## How to Run the Script

1.  **Download the Project:**
    *   Ensure you have all project files, including `Install-And-Run-BlinkNews.ps1`, in a folder on your computer.

2.  **Open PowerShell as Administrator:**
    *   Search for "PowerShell" in the Start Menu.
    *   Right-click on "Windows PowerShell" (or "PowerShell 7").
    *   Select "Run as administrator".

3.  **Navigate to the Project Directory:**
    *   In the PowerShell window, use the `cd` command to go to the folder where you saved the project. For example:
        ```powershell
        cd "D:\Path\To\Your\BLINK-NEWS"
        ```

4.  **Check Execution Policy (Script handles this, but for awareness):**
    *   PowerShell has an execution policy that might prevent scripts from running. The `Install-And-Run-BlinkNews.ps1` script will attempt to set the policy to `RemoteSigned` for its own session.
    *   If it fails to do this automatically, it will provide you with clear instructions on how to set it manually using `Set-ExecutionPolicy RemoteSigned -Scope CurrentUser` (you'd run this in another Administrator PowerShell window).

5.  **Run the Installer Script:**
    *   Execute the script by typing its name:
        ```powershell
        .\Install-And-Run-BlinkNews.ps1
        ```

## What the Script Does

*   **Checks for `winget`:** If not found, it guides you to install "App Installer" from the Microsoft Store.
*   **Installs Python:** If a suitable version of Python (3.9+) is not found, it attempts to install it via `winget`.
*   **Installs Node.js (LTS):** If Node.js is not found, it attempts to install it via `winget`. (npm is included with Node.js).
*   **Sets up Python Virtual Environment:** Creates a `blink_venv` folder and installs Python dependencies from `requirements.txt`.
*   **Installs `pnpm`:** Installs `pnpm` globally using `npm`.
*   **Launches Applications:** Starts the backend (Flask) and frontend (Vite) servers in new, separate PowerShell windows.

## After Running the Script

*   **Follow On-Screen Instructions:** The script will provide messages about its progress, potential warnings, or errors.
*   **Administrator Prompts:** If `winget` needs to install software, you might see User Account Control (UAC) prompts asking for permission. Please approve these.
*   **New Windows:** Two new PowerShell windows will open:
    *   One for the **Backend**.
    *   One for the **Frontend**.
*   **Accessing the Application:**
    *   Look at the **Frontend** window. After it compiles, it will display a "Local:" URL, typically `http://localhost:5173`.
    *   Open this URL in your web browser.
*   **Stopping the Application:**
    *   To stop BLINK NEWS, go to **each** of the two new PowerShell windows that were opened for the backend and frontend.
    *   Press `CTRL+C` in each window. You might need to confirm by typing `Y` or `N`.

## Troubleshooting

*   **Execution Policy Issues:** If the script complains about execution policy even after attempting to set it, ensure you run the `Set-ExecutionPolicy RemoteSigned -Scope CurrentUser` command in an Administrator PowerShell window and then try the script again.
*   **`winget` not found:** Ensure "App Installer" is installed and updated from the Microsoft Store.
*   **PATH Environment Variable Issues:** If Python, Node.js, or `pnpm` are installed by the script but still not found in a *new* terminal session immediately after, you might need to restart Windows or sign out and sign back in for all PATH changes to take full effect system-wide. The script attempts to update PATH for its own session, but this doesn't always propagate to new, unrelated terminal windows instantly.
*   **Firewall:** Your firewall might ask for permission for Python or Node.js to access the network. Allow this if prompted.

This script aims to simplify the setup process significantly. Please report any issues encountered.
