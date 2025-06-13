<#
.SYNOPSIS
    Instala las dependencias locales para el desarrollo de BLINK NEWS.
.DESCRIPTION
    Este script es una herramienta de CONFIGURACIÓN DE UN SOLO USO.
    1. Instala Python y Node.js usando winget si no existen.
    2. Crea el entorno virtual de Python 'blink_venv'.
    3. Instala las dependencias de 'requirements.txt' en el venv.
    NO EJECUTA LA APLICACIÓN. Para eso, sigue las instrucciones al final.
#>

# --- Configuración Inicial ---
$ErrorActionPreference = 'Stop'
Write-Host "--- BLINK NEWS - Asistente de Instalación de Entorno Local ---" -ForegroundColor Green

# Attempt to set Execution Policy for the current process to allow script execution
try {
    $currentProcessPolicy = Get-ExecutionPolicy -Scope Process -ErrorAction SilentlyContinue
    if ($currentProcessPolicy -ne "RemoteSigned" -and $currentProcessPolicy -ne "Unrestricted" -and $currentProcessPolicy -ne "Bypass") {
        Write-Host "Attempting to set Execution Policy to 'RemoteSigned' for the current PowerShell process..."
        Set-ExecutionPolicy RemoteSigned -Scope Process -Force -ErrorAction Stop
        Write-Host "Execution policy for current process set to 'RemoteSigned'. This change only affects this session."
    }
} catch {
    Write-Warning "----------------------------------------------------------------------------------"
    Write-Warning "IMPORTANT: Failed to automatically set PowerShell Execution Policy for this session."
    Write-Warning "If script execution is blocked, open PowerShell AS ADMINISTRATOR and run:"
    Write-Warning "  Set-ExecutionPolicy RemoteSigned -Scope CurrentUser  (Recommended)"
    Write-Warning "Then, re-run this script."
    Write-Warning "----------------------------------------------------------------------------------"
    # Continue if this fails, user might have it set correctly already or will do it manually.
}

Function Test-Admin {
    try {
        $windowsIdentity = [System.Security.Principal.WindowsIdentity]::GetCurrent()
        $windowsPrincipal = New-Object System.Security.Principal.WindowsPrincipal($windowsIdentity)
        return $windowsPrincipal.IsInRole([System.Security.Principal.WindowsBuiltinRole]::Administrator)
    } catch {
        Write-Warning "Could not determine if running as Administrator. Winget installs might require it."
        return $false # Assume not admin if check fails
    }
}

if (-not (Test-Admin)) {
    Write-Warning "This script may need Administrator privileges to install software using winget."
    Write-Warning "If installations fail, please try running this script as an Administrator."
}

# --- Comprobaciones de Dependencias (Python, Node.js) ---

Write-Host ""
Write-Host "Paso 1: Comprobando Winget..." -ForegroundColor Cyan
$wingetPath = Get-Command winget -ErrorAction SilentlyContinue
if ($null -eq $wingetPath) {
    Write-Warning "----------------------------------------------------------------------------------"
    Write-Warning "ERROR: winget command not found."
    Write-Warning "winget is required to automatically install Python and Node.js."
    Write-Host "How to install winget (usually included in modern Windows):"
    Write-Host "1. Open the Microsoft Store."
    Write-Host "2. Search for 'App Installer'."
    Write-Host "3. Install or Update it (Publisher: Microsoft Corporation)."
    Write-Host "After installing/updating App Installer, please re-run this script."
    Write-Warning "----------------------------------------------------------------------------------"
    Read-Host -Prompt "Press Enter to exit script"
    exit 1
} else {
    Write-Host "Winget encontrado: $($wingetPath.Source)"
}

Write-Host ""
Write-Host "Paso 2: Comprobando Python..." -ForegroundColor Cyan
$pythonInstalled = $false
$pythonExeToUse = $null
try {
    # Check for python3 first, then python
    $pythonExePath = Get-Command python3 -ErrorAction SilentlyContinue
    if ($null -eq $pythonExePath) {
        $pythonExePath = Get-Command python -ErrorAction SilentlyContinue
    }

    if ($null -ne $pythonExePath) {
        $pythonVersionOutput = Invoke-Expression "$($pythonExePath.Source) --version" 2>&1
        Write-Host "Python encontrado: $($pythonExePath.Source) - Versión: $pythonVersionOutput"
        # Simple check if output contains "Python 3.11" - adjust if more specific parsing needed
        if ($pythonVersionOutput -match "Python 3\.11") {
            Write-Host "Python 3.11 ya está instalado."
            $pythonInstalled = $true
            $pythonExeToUse = $pythonExePath.Source
        } else {
            Write-Warning "Python encontrado, pero no es la versión 3.11. Se intentará instalar la versión correcta."
        }
    } else {
         Write-Host "Python no encontrado en el PATH."
    }
} catch {
    Write-Warning "No se pudo verificar la versión de Python existente. Error: $($_.Exception.Message)"
}

if (-not $pythonInstalled) {
    Write-Host "Intentando instalar Python 3.11 con winget..."
    Write-Host "(Esto puede requerir privilegios de Administrador y tomar unos minutos)"
    try {
        # Using the specific ID for Python 3.11
        winget install --id Python.Python.3.11 -e --accept-source-agreements --accept-package-agreements --scope machine --silent
        Write-Host "Instalación de Python 3.11 vía winget completada."
        Write-Host "Refrescando variables de entorno para detectar la nueva instalación de Python..."
        $env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")

        $pythonExePath = Get-Command python3 -ErrorAction SilentlyContinue
        if ($null -eq $pythonExePath) {
            $pythonExePath = Get-Command python -ErrorAction SilentlyContinue
        }

        if ($null -ne $pythonExePath) {
            Write-Host "Python 3.11 instalado y encontrado: $($pythonExePath.Source)"
            Invoke-Expression "$($pythonExePath.Source) --version"
            $pythonInstalled = $true
            $pythonExeToUse = $pythonExePath.Source
        } else {
            Write-Warning "----------------------------------------------------------------------------------"
            Write-Warning "ERROR: Python 3.11 fue instalado por winget, pero aún no se encuentra en el PATH."
            Write-Warning "ACCIÓN REQUERIDA: Por favor, CIERRA y REABRE esta terminal/PowerShell y VUELVE A EJECUTAR este script."
            Write-Warning "Si el problema persiste, asegúrate que el directorio de instalación de Python esté en tu PATH."
            Write-Warning "----------------------------------------------------------------------------------"
            Read-Host -Prompt "Presiona Enter para salir del script"
            exit 1
        }
    } catch {
        Write-Error "----------------------------------------------------------------------------------"
        Write-Error "ERROR: Falló la instalación de Python 3.11 con winget."
        Write-Error "Detalles: $($_.Exception.Message)"
        Write-Host "Por favor, intenta instalar Python 3.11 manualmente y asegúrate que esté en tu PATH."
        Write-Error "----------------------------------------------------------------------------------"
        Read-Host -Prompt "Presiona Enter para salir del script"
        exit 1
    }
}
# Ensure $pythonExeToUse is set for venv creation
if ($null -eq $pythonExeToUse) {
    $pythonExeToUse = Get-Command python3 -ErrorAction SilentlyContinue
    if ($null -eq $pythonExeToUse) {
        $pythonExeToUse = Get-Command python -ErrorAction SilentlyContinue
    }
    if ($null -eq $pythonExeToUse) {
         Write-Error "No se pudo determinar el ejecutable de Python a usar. Saliendo."
         exit 1
    }
    $pythonExeToUse = $pythonExeToUse.Source
}


Write-Host ""
Write-Host "Paso 3: Comprobando Node.js y pnpm..." -ForegroundColor Cyan
$nodeInstalled = $false
$npmInstalled = $false
$pnpmInstalled = $false

try {
    $nodeExePath = Get-Command node -ErrorAction SilentlyContinue
    $npmExePath = Get-Command npm -ErrorAction SilentlyContinue

    if ($null -ne $nodeExePath) {
        Write-Host "Node.js encontrado: $($nodeExePath.Source)"
        node --version
        $nodeInstalled = $true
    } else {
        Write-Host "Node.js no encontrado."
    }
    if ($null -ne $npmExePath) {
        Write-Host "npm encontrado: $($npmExePath.Source)"
        npm --version
        $npmInstalled = $true
    } else {
        Write-Host "npm no encontrado (usualmente viene con Node.js)."
    }
} catch {
    Write-Warning "No se pudo verificar la versión de Node.js o npm. Error: $($_.Exception.Message)"
}

if (-not $nodeInstalled -or -not $npmInstalled) {
    Write-Host "Intentando instalar la última versión LTS de Node.js (incluye npm) con winget..."
    Write-Host "(Esto puede requerir privilegios de Administrador y tomar unos minutos)"
    try {
        winget install --id OpenJS.NodeJS.LTS -e --accept-source-agreements --accept-package-agreements --scope machine --silent
        Write-Host "Instalación de Node.js LTS vía winget completada."
        Write-Host "Refrescando variables de entorno para detectar la nueva instalación de Node.js/npm..."
        $env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")

        $nodeExePath = Get-Command node -ErrorAction SilentlyContinue
        $npmExePath = Get-Command npm -ErrorAction SilentlyContinue

        if (($null -ne $nodeExePath) -and ($null -ne $npmExePath)) {
            Write-Host "Node.js instalado y encontrado: $($nodeExePath.Source)"
            node --version
            Write-Host "npm instalado y encontrado: $($npmExePath.Source)"
            npm --version
            $nodeInstalled = $true
            $npmInstalled = $true
        } else {
            Write-Warning "----------------------------------------------------------------------------------"
            Write-Warning "ERROR: Node.js/npm fue instalado por winget, pero aún no se encuentra en el PATH."
            Write-Warning "ACCIÓN REQUERIDA: Por favor, CIERRA y REABRE esta terminal/PowerShell y VUELVE A EJECUTAR este script."
            Write-Warning "Si el problema persiste, asegúrate que el directorio de instalación de Node.js esté en tu PATH (ej. C:\Program Files\nodejs\)."
            Write-Warning "----------------------------------------------------------------------------------"
            Read-Host -Prompt "Presiona Enter para salir del script"
            exit 1
        }
    } catch {
        Write-Error "----------------------------------------------------------------------------------"
        Write-Error "ERROR: Falló la instalación de Node.js LTS con winget."
        Write-Error "Detalles: $($_.Exception.Message)"
        Write-Host "Por favor, intenta instalar Node.js LTS manualmente y asegúrate que él y npm estén en tu PATH."
        Write-Error "----------------------------------------------------------------------------------"
        Read-Host -Prompt "Presiona Enter para salir del script"
        exit 1
    }
}

# Check for pnpm
if ($nodeInstalled -and $npmInstalled) { # Only try to install pnpm if Node/npm are present
    $pnpmExePath = Get-Command pnpm -ErrorAction SilentlyContinue
    if ($null -ne $pnpmExePath) {
        Write-Host "pnpm encontrado: $($pnpmExePath.Source)"
        pnpm --version
        $pnpmInstalled = $true
    } else {
        Write-Host "pnpm no encontrado. Intentando instalar pnpm globalmente con npm..."
        try {
            npm install -g pnpm
            Write-Host "Comando de instalación global de pnpm ejecutado."
            Write-Host "Refrescando variables de entorno para detectar la nueva instalación de pnpm..."
            $env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User") + ";" + ([System.Environment]::GetEnvironmentVariable("APPDATA", "User") + "\npm") # Common global path

            $pnpmExePath = Get-Command pnpm -ErrorAction SilentlyContinue
            if ($null -ne $pnpmExePath) {
                Write-Host "pnpm instalado y encontrado: $($pnpmExePath.Source)"
                pnpm --version
                $pnpmInstalled = $true
            } else {
                Write-Warning "----------------------------------------------------------------------------------"
                Write-Warning "ADVERTENCIA: pnpm fue instalado por npm, pero aún no se encuentra en el PATH."
                Write-Warning "Puede que necesites CIERRA y REABRE esta terminal/PowerShell."
                Write-Warning "Si el problema persiste, encuentra la ruta global de npm (npm config get prefix) y añádela al PATH."
                Write-Warning "----------------------------------------------------------------------------------"
            }
        } catch {
            Write-Error "ERROR: Falló la instalación global de pnpm con npm. Detalles: $($_.Exception.Message)"
            Write-Warning "Por favor, intenta instalar pnpm manualmente con: npm install -g pnpm"
        }
    }
}


# --- Creación del Entorno Virtual y Dependencias de Python ---
Write-Host ""
Write-Host "Paso 4: Configurando el entorno virtual de Python ('blink_venv')..." -ForegroundColor Cyan
$VenvDir = "blink_venv"
$VenvPath = Join-Path -Path $PSScriptRoot -ChildPath $VenvDir
$PythonFromVenv = Join-Path -Path $VenvPath -ChildPath "Scripts\python.exe"

if (-not (Test-Path $PythonFromVenv)) {
    Write-Host "Creando entorno virtual en '$VenvDir' usando '$pythonExeToUse'..."
    try {
        & $pythonExeToUse -m venv $VenvPath
        Write-Host "Entorno virtual creado."
    } catch {
        Write-Error "ERROR: No se pudo crear el entorno virtual. Asegúrate de que Python ($pythonExeToUse) esté instalado y sea accesible. Error: $($_.Exception.Message)"
        exit 1
    }
} else {
    Write-Host "El entorno virtual 'blink_venv' ya existe en '$VenvPath'."
}

Write-Host "Instalando dependencias de Python desde requirements.txt en 'blink_venv'..."
try {
    & $PythonFromVenv -m pip install --upgrade pip
    & $PythonFromVenv -m pip install -r (Join-Path -Path $PSScriptRoot -ChildPath "requirements.txt")
    Write-Host "Dependencias de Python instaladas correctamente en 'blink_venv'." -ForegroundColor Green
} catch {
    Write-Error "ERROR: Falló la instalación de dependencias de Python. Revisa el error: $($_.Exception.Message)"
    exit 1
}

# --- Dependencias del Frontend ---
Write-Host ""
Write-Host "Paso 5: Configurando dependencias del frontend..." -ForegroundColor Cyan
$FrontendDir = Join-Path -Path $PSScriptRoot -ChildPath "news-blink-frontend"

if ($pnpmInstalled -and ($null -ne (Get-Command pnpm -ErrorAction SilentlyContinue))) {
    Write-Host "pnpm encontrado. Instalando dependencias del frontend en '$FrontendDir'..."
    try {
        Push-Location $FrontendDir
        pnpm install
        Pop-Location
        Write-Host "Dependencias del frontend instaladas correctamente." -ForegroundColor Green
    } catch {
        Write-Error "ERROR: 'pnpm install' falló en '$FrontendDir'. Revisa el error: $($_.Exception.Message)"
        # No salir, solo advertir.
    }
} else {
    Write-Warning "ADVERTENCIA: pnpm no está disponible o no se pudo verificar."
    Write-Warning "Por favor, asegúrate de que pnpm esté instalado ('npm install -g pnpm') y luego ejecuta 'pnpm install' manualmente en la carpeta '$FrontendDir'."
}

# --- INSTRUCCIONES FINALES ---
Write-Host ""
Write-Host "-----------------------------------------------------------------" -ForegroundColor Yellow
Write-Host "  ✅ ¡LA CONFIGURACIÓN DEL ENTORNO LOCAL HA TERMINADO! ✅" -ForegroundColor Yellow
Write-Host "-----------------------------------------------------------------" -ForegroundColor Yellow
Write-Host ""
Write-Host "Este script NO inicia la aplicación para evitar conflictos."
Write-Host ""
Write-Host "--- MÉTODO RECOMENDADO PARA EJECUTAR LA APLICACIÓN ---" -ForegroundColor Green
Write-Host "1. Asegúrate de que Docker Desktop esté corriendo."
Write-Host "2. En una terminal, en la raíz del proyecto, ejecuta: docker-compose up --build"
Write-Host "3. En una SEGUNDA terminal, ve a 'news-blink-frontend' y ejecuta: pnpm run dev"
Write-Host ""
Write-Host "--- MÉTODO ALTERNATIVO (LOCAL) ---" -ForegroundColor Cyan
Write-Host "1. Abre una terminal y activa el entorno: .link_venv\Scriptsctivate.ps1"
Write-Host "   (Si usas cmd, es: blink_venv\Scriptsctivate.bat)"
Write-Host "2. En esa terminal (verás '(blink_venv)' al inicio), ejecuta: python news-blink-backend/src/app.py"
Write-Host "3. En una SEGUNDA terminal, ve a 'news-blink-frontend' y ejecuta: pnpm run dev"
Write-Host ""

Read-Host -Prompt "Presiona Enter para finalizar este script de instalación"

```
