import subprocess
import os
import sys
import threading
import signal
import time
import shutil # Ensure shutil is imported

# List to keep track of Popen objects for cleanup
processes = []
process_threads = [] # Keep track of threads

def run_command(command, name, cwd=None, env=None):
    # ... (rest of the function as previously defined and tested) ...
    global processes
    print(f"[{name}] Starting command: {' '.join(command)} in {cwd or os.getcwd()}")
    try:
        process_env = os.environ.copy()
        if env:
            process_env.update(env)

        process = subprocess.Popen(
            command,
            cwd=cwd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=process_env,
        )
        processes.append(process)

        def stream_output(pipe, prefix):
            try:
                for line_bytes in iter(pipe.readline, b''):
                    line_str = line_bytes.decode('utf-8', 'replace').rstrip()
                    print(f"[{prefix}] {line_str}")
                    sys.stdout.flush()
            except Exception as e:
                print(f"[{prefix}] Error reading output: {e}")
            finally:
                pipe.close()

        stdout_thread = threading.Thread(target=stream_output, args=(process.stdout, name))
        stderr_thread = threading.Thread(target=stream_output, args=(process.stderr, f"{name}-ERR"))
        stdout_thread.daemon = True
        stderr_thread.daemon = True
        stdout_thread.start()
        stderr_thread.start()
        print(f"[{name}] Process started with PID: {process.pid}")
        return process
    except FileNotFoundError:
        print(f"[{name}-ERROR] Command not found: {command[0]}. Please ensure it is installed and in PATH.")
        return None
    except Exception as e:
        print(f"[{name}-ERROR] Failed to start command {' '.join(command)}: {e}")
        return None

def signal_handler(sig, frame):
    # ... (rest of the function as previously defined and tested) ...
    print("\nShutting down processes...")
    for p in reversed(processes):
        if p.poll() is None:
            print(f"Terminating process {p.pid}...")
            try:
                p.terminate()
            except Exception as e:
                print(f"Error terminating process {p.pid}: {e}")
    timeout_seconds = 5
    for p in reversed(processes):
        if p.poll() is None:
            try:
                p.wait(timeout=timeout_seconds)
            except subprocess.TimeoutExpired:
                print(f"Process {p.pid} did not terminate in time, killing...")
                p.kill()
            except Exception as e:
                print(f"Error waiting for process {p.pid}: {e}")
    print("All processes have been signaled.")
    for t in process_threads:
        if t.is_alive():
            t.join(timeout=1)
    sys.exit(0)

if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal_handler)

    backend_proc = None
    frontend_proc = None

    backend_command = None
    backend_cwd = None
    command_backend_console = ['news-blink-backend']

    # Check if running in a virtual environment
    if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print(f"[SYSTEM] Virtual environment detected at: {sys.prefix}")
        if os.name == 'nt':
            venv_executable_path = os.path.join(sys.prefix, 'Scripts', 'news-blink-backend.exe')
        else: # POSIX (Linux, macOS, Git Bash)
            venv_executable_path = os.path.join(sys.prefix, 'bin', 'news-blink-backend')

        print(f"[SYSTEM] Attempting to use venv executable: {venv_executable_path}")
        if os.path.exists(venv_executable_path):
            print(f"[SYSTEM] Found venv executable: {venv_executable_path}")
            backend_command = [venv_executable_path]
        else:
            print(f"[SYSTEM] Venv executable not found at: {venv_executable_path}")
    else:
        print("[SYSTEM] No virtual environment detected by sys.prefix inspection.")

    if not backend_command:
        print("[SYSTEM] Venv-specific backend script not found or not in a venv. Trying PATH-based lookup.")
        found_path = shutil.which(command_backend_console[0])
        if found_path:
            print(f"[SYSTEM] '{command_backend_console[0]}' command found via shutil.which at: {found_path}")
            backend_command = command_backend_console
        else:
            print(f"[SYSTEM] shutil.which did not find '{command_backend_console[0]}'. Trying original 'which'/'where'.")
            try:
                check_cmd_str = ['which', command_backend_console[0]] if os.name != 'nt' else ['where', command_backend_console[0]]
                subprocess.check_output(check_cmd_str, shell=(os.name == 'nt' and check_cmd_str[0] == 'where'), stderr=subprocess.DEVNULL)
                print(f"[SYSTEM] '{command_backend_console[0]}' command seems available via PATH (using 'which'/'where').")
                backend_command = command_backend_console
            except (subprocess.CalledProcessError, FileNotFoundError):
                print(f"[SYSTEM] '{command_backend_console[0]}' command not found via PATH. Falling back to app.py.")
                backend_command = [sys.executable, 'app.py']
                backend_cwd = os.path.join('news-blink-backend', 'src')
                if not os.path.exists(os.path.join(backend_cwd, 'app.py')):
                    print(f"[SYSTEM-ERROR] Fallback app.py not found at {os.path.join(backend_cwd, 'app.py')}. Backend cannot start.")
                    backend_command = None

    backend_env = None
    if backend_command:
        def start_backend_task():
            global backend_proc
            backend_proc = run_command(backend_command, "BACKEND", backend_cwd, backend_env)
        backend_run_thread = threading.Thread(target=start_backend_task, daemon=True)
        process_threads.append(backend_run_thread)
        backend_run_thread.start()

    frontend_command = ['pnpm', 'run', 'dev']
    frontend_cwd = 'news-blink-frontend'
    if not os.path.isdir(frontend_cwd):
        print(f"[SYSTEM-ERROR] Frontend directory '{frontend_cwd}' not found. Cannot start frontend.")
    else:
        try:
            subprocess.check_output(['pnpm', '--version'], shell=(os.name == 'nt'), stderr=subprocess.DEVNULL)
            print("[SYSTEM] pnpm found. Starting frontend.")
            def start_frontend_task():
                global frontend_proc
                frontend_proc = run_command(frontend_command, "FRONTEND", frontend_cwd)
            frontend_run_thread = threading.Thread(target=start_frontend_task, daemon=True)
            process_threads.append(frontend_run_thread)
            frontend_run_thread.start()
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("[SYSTEM-ERROR] 'pnpm' command not found. Please install pnpm (e.g., 'npm install -g pnpm') and ensure it's in PATH.")
            print("[SYSTEM-ERROR] Frontend will not be started.")

    print("[SYSTEM] Backend and Frontend processes initiated. Press Ctrl+C to shut down.")
    try:
        while True:
            all_processes_finished_or_failed = True
            if not processes:
                if not any(t.is_alive() for t in process_threads if t is not threading.current_thread()):
                    print("[SYSTEM] No processes were started and launcher threads are done. Exiting.")
                    break
                else:
                    all_processes_finished_or_failed = False
            else:
                active_processes = 0
                for p in processes:
                    if p is None: continue
                    if p.poll() is None:
                        all_processes_finished_or_failed = False
                        active_processes +=1
                if all_processes_finished_or_failed:
                    print("[SYSTEM] All managed processes seem to have terminated on their own. Exiting.")
                    break
                if active_processes == 0 and any(t.is_alive() for t in process_threads if t is not threading.current_thread()):
                    all_processes_finished_or_failed = False
            if all_processes_finished_or_failed and not any(t.is_alive() for t in process_threads if t is not threading.current_thread()):
                print("[SYSTEM] All processes and launcher threads finished. Exiting.")
                break
            time.sleep(1)
    except KeyboardInterrupt:
        signal_handler(signal.SIGINT, None)
    finally:
        active_procs_at_exit = [p for p in processes if p and p.poll() is None]
        if active_procs_at_exit:
             print("[SYSTEM] Main loop exited, ensuring process cleanup for running processes...")
             signal_handler(signal.SIGINT, None) # Trigger cleanup
        else:
            print("[SYSTEM] Main loop exited, no running processes detected that need signaling.")
        print("[SYSTEM] Exiting main script.")
