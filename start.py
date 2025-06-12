import subprocess
import os
import sys
import threading
import signal
import time

# List to keep track of Popen objects for cleanup
processes = []
process_threads = [] # Keep track of threads

def run_command(command, name, cwd=None, env=None):
    """
    Runs a command in a subprocess and prints its output prefixed with its name.
    Returns the Popen object.
    """
    global processes
    print(f"[{name}] Starting command: {' '.join(command)} in {cwd or os.getcwd()}")
    try:
        # Create a new environment if specific env vars are needed, otherwise inherit
        process_env = os.environ.copy()
        if env:
            process_env.update(env)

        process = subprocess.Popen(
            command,
            cwd=cwd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=process_env,
            # Using bufsize=1 for line buffering.
            # universal_newlines=True is an alternative but text=True is preferred in Python 3.7+
            # However, to manually decode and handle errors, we'll read bytes.
        )
        processes.append(process) # Add to global list for signal handling

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

        stdout_thread.daemon = True # Daemon threads exit when the main program exits
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
    """Handles SIGINT (Ctrl+C) to gracefully shut down subprocesses."""
    print("\nShutting down processes...")
    for p in reversed(processes): # Terminate in reverse order of startup
        if p.poll() is None: # If process is still running
            print(f"Terminating process {p.pid}...")
            try:
                p.terminate() # Send SIGTERM
            except Exception as e:
                print(f"Error terminating process {p.pid}: {e}")

    # Wait for processes to terminate
    # Set a timeout for waiting, e.g., 5 seconds per process
    timeout_seconds = 5
    for p in reversed(processes):
        if p.poll() is None:
            try:
                p.wait(timeout=timeout_seconds)
            except subprocess.TimeoutExpired:
                print(f"Process {p.pid} did not terminate in time, killing...")
                p.kill() # Force kill if terminate + wait fails
            except Exception as e:
                print(f"Error waiting for process {p.pid}: {e}")

    print("All processes have been signaled.")
    # Wait for I/O threads to finish (optional, as they are daemons)
    # For cleaner exit, especially if they write to files or network
    for t in process_threads:
        if t.is_alive():
            t.join(timeout=1) # Give threads a moment to finish

    sys.exit(0)

if __name__ == "__main__":
    # Register signal handler for SIGINT
    signal.signal(signal.SIGINT, signal_handler)

    backend_proc = None
    frontend_proc = None

    # 1. Start Backend
    backend_cwd = None
    backend_env = None # Could be set e.g. {'FLASK_ENV': 'development'}

    # Try starting backend with the console script first
    command_backend_console = ['news-blink-backend']
    print(f"[SYSTEM] Attempting to start backend using console script: {' '.join(command_backend_console)}")

    # We need to run this attempt in a way that we can catch FileNotFoundError specifically
    # for the command itself, not for run_command. So, a preliminary check or structure run_command.
    # For simplicity here, run_command already prints a FileNotFoundError.
    # We'll check the return value of run_command.

    # To truly distinguish between 'command not found' and 'command failed to start but was found',
    # Popen is called inside run_command. So run_command will return None on FileNotFoundError.

    # backend_thread = threading.Thread(target=run_command, args=(command_backend_console, "BACKEND", backend_cwd, backend_env), daemon=True)
    # process_threads.append(backend_thread)
    # backend_thread.start()
    # backend_thread.join(timeout=0.5) # Give it a moment to start or fail with FileNotFoundError

    # Check if backend started (processes list would be populated by run_command)
    # This is a bit tricky because run_command itself handles the Popen.
    # A better way: run_command should raise an exception on FileNotFoundError for the Popen call itself.
    # For now, let's assume if the processes list is empty after trying to start backend, it failed.

    # Simplified check: if the first process in `processes` (if any) corresponds to the backend and failed early.
    # This logic is getting complicated due to how `run_command` is structured.
    # A simpler way for this script:
    # Try Popen directly here for the first attempt to catch FileNotFoundError.

    try:
        # Try to see if 'news-blink-backend' is resolvable by the system (quick check)
        # This doesn't run it, just checks if the system can find it.
        # Added shell=True for Windows compatibility with 'where' and to handle PATH correctly.
        subprocess.check_output(['which', 'news-blink-backend'] if os.name != 'nt' else ['where', 'news-blink-backend'], shell=(os.name == 'nt'), stderr=subprocess.DEVNULL)
        print("[SYSTEM] 'news-blink-backend' command seems available.")
        backend_command = command_backend_console
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("[SYSTEM] 'news-blink-backend' command not found or 'which'/'where' failed. Falling back to app.py.")
        backend_command = [sys.executable, 'app.py']
        backend_cwd = os.path.join('news-blink-backend', 'src')
        if not os.path.exists(os.path.join(backend_cwd, 'app.py')):
            print(f"[SYSTEM-ERROR] Fallback app.py not found at {os.path.join(backend_cwd, 'app.py')}. Backend cannot start.")
            backend_command = None # Prevent starting

    if backend_command:
        # Using a lambda to assign the result of run_command to the global backend_proc
        # This is not ideal; a class-based approach or a shared dictionary/queue would be cleaner for managing procs.
        # For this script, this direct update to globals() is used for simplicity.
        def start_backend_task():
            global backend_proc
            backend_proc = run_command(backend_command, "BACKEND", backend_cwd, backend_env)

        backend_run_thread = threading.Thread(target=start_backend_task, daemon=True)
        process_threads.append(backend_run_thread)
        backend_run_thread.start()

    # 2. Start Frontend
    frontend_command = ['pnpm', 'run', 'dev']
    frontend_cwd = 'news-blink-frontend'

    if not os.path.isdir(frontend_cwd):
        print(f"[SYSTEM-ERROR] Frontend directory '{frontend_cwd}' not found. Cannot start frontend.")
    else:
        # Check for pnpm first
        try:
            # Added shell=True for Windows compatibility with 'pnpm.cmd' and to handle PATH correctly.
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


    # Keep the main thread alive until SIGINT
    print("[SYSTEM] Backend and Frontend processes initiated. Press Ctrl+C to shut down.")
    try:
        while True:
            all_processes_finished_or_failed = True
            if not processes: # No processes were even attempted to start (e.g. all pre-checks failed)
                 # Check if the threads that were supposed to start them are also done.
                if not any(t.is_alive() for t in process_threads if t is not threading.current_thread()):
                    print("[SYSTEM] No processes were started and launcher threads are done. Exiting.")
                    break # Exit if no processes were ever added and threads are done.
                else:
                    all_processes_finished_or_failed = False # Launcher threads still running
            else: # Processes were attempted
                active_processes = 0
                for p in processes:
                    if p is None: # Process failed to start (e.g. FileNotFoundError in run_command)
                        continue
                    if p.poll() is None: # Process is still running
                        all_processes_finished_or_failed = False
                        active_processes +=1

                if all_processes_finished_or_failed:
                    print("[SYSTEM] All managed processes seem to have terminated on their own. Exiting.")
                    break
                # If no active processes but threads still running (e.g. initial startup phase)
                if active_processes == 0 and any(t.is_alive() for t in process_threads if t is not threading.current_thread()):
                    all_processes_finished_or_failed = False # still starting up

            if all_processes_finished_or_failed and not any(t.is_alive() for t in process_threads if t is not threading.current_thread()):
                print("[SYSTEM] All processes and launcher threads finished. Exiting.")
                break


            time.sleep(1) # Keep main thread alive, periodically checking
    except KeyboardInterrupt: # This is redundant if signal_handler works for SIGINT
        signal_handler(signal.SIGINT, None) # Should be caught by signal_handler
    finally:
        # Ensure cleanup if loop broken by other means than SIGINT
        # Check if any process in the global list is still running
        active_procs_at_exit = [p for p in processes if p and p.poll() is None]
        if active_procs_at_exit:
             print("[SYSTEM] Main loop exited, ensuring process cleanup for running processes...")
             signal_handler(signal.SIGINT, None) # Trigger cleanup
        else:
            print("[SYSTEM] Main loop exited, no running processes detected that need signaling.")
        print("[SYSTEM] Exiting main script.")
