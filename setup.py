import os
import subprocess
from setuptools import setup, find_packages
from setuptools.command.install import install

class CustomInstallCommand(install):
    """Customized setuptools install command."""
    def run(self):
        # Attempt to install pnpm globally
        try:
            print("Attempting to install pnpm globally...")
            # Using shell=True can be a security risk if command components are from untrusted input.
            # Here, 'npm install -g pnpm' is static, reducing risk.
            # On some systems, npm might be a script that requires shell, or pnpm might be installed via shell.
            npm_command = "npm install -g pnpm"
            pnpm_install_proc = subprocess.run(npm_command, shell=True, check=False, capture_output=True, text=True)
            if pnpm_install_proc.returncode == 0:
                print("pnpm global install command executed successfully (or pnpm already installed).")
            else:
                print(f"pnpm global install command failed. STDOUT: {pnpm_install_proc.stdout} STDERR: {pnpm_install_proc.stderr}")

            # Verify pnpm installation
            pnpm_check = subprocess.run(['pnpm', '--version'], capture_output=True, text=True, shell=True)
            if pnpm_check.returncode == 0:
                print(f"pnpm successfully installed or already present: version {pnpm_check.stdout.strip()}")
            else:
                print("pnpm not found after installation attempt. Please install pnpm manually (e.g., 'npm install -g pnpm') and ensure it's in your PATH.")
        except FileNotFoundError:
            print("npm command not found. Please ensure Node.js and npm are installed and in your PATH.")
        except Exception as e:
            print(f"An error occurred during pnpm installation: {e}")

        # Store the original directory
        original_dir = os.getcwd()
        frontend_dir = os.path.join(original_dir, 'news-blink-frontend')

        if os.path.isdir(frontend_dir):
            try:
                print(f"Changing directory to {frontend_dir}")
                os.chdir(frontend_dir)

                print("Running 'pnpm install' in news-blink-frontend...")
                # Using shell=True for pnpm as well, as pnpm might be a .cmd or shell script,
                # especially after being installed by npm.
                pnpm_install_result = subprocess.run('pnpm install', shell=True, check=True, capture_output=True, text=True)
                print(f"pnpm install completed successfully in news-blink-frontend. STDOUT: {pnpm_install_result.stdout}")

            except subprocess.CalledProcessError as e:
                print(f"Error during 'pnpm install' in {frontend_dir}. Return code: {e.returncode}")
                print(f"STDOUT: {e.stdout}")
                print(f"STDERR: {e.stderr}")
                print("Please ensure pnpm is installed correctly and the frontend dependencies are valid.")
            except FileNotFoundError:
                print(f"pnpm command not found in {frontend_dir} or PATH. Make sure pnpm is installed (e.g. npm install -g pnpm).")
            except Exception as e:
                print(f"An unexpected error occurred in frontend setup: {e}")
            finally:
                print(f"Changing back to original directory: {original_dir}")
                os.chdir(original_dir)
        else:
            print(f"Frontend directory {frontend_dir} not found. Skipping pnpm install.")

        # Run the original install command
        print("Proceeding with standard Python package installation...")
        super().run()
        print("Standard Python package installation finished.")

setup(
    name='news-blink-backend',
    version='0.1.0',
    # Corrected package_dir and find_packages path
    packages=find_packages(where='news-blink-backend/src'),
    package_dir={'': 'news-blink-backend/src'},
    include_package_data=True,
    install_requires=[
        'Flask==2.3.3',
        'Flask-CORS==4.0.0',
        'requests==2.31.0',
        'beautifulsoup4==4.12.2',
        'nltk==3.8.1',
        'ollama==0.1.7',
    ],
    entry_points={
        'console_scripts': [
            # Assuming app:create_app refers to news-blink-backend/src/app.py
            'news-blink-backend=app:create_app',
        ],
    },
    python_requires='>=3.9',
    cmdclass={
        'install': CustomInstallCommand,
    },
)
