from setuptools import setup, find_packages

setup(
    name=\'news-blink-backend\',
    version=\'0.1.0\',
    packages=find_packages(where=\'src\'),
    package_dir={\'\': \'src\'}, # Indica que los paquetes están en el directorio src
    include_package_data=True,
    install_requires=[
        \'Flask==2.3.3\',
        \'Flask-CORS==4.0.0\',
        \'requests==2.31.0\',
        \'beautifulsoup4==4.12.2\',
        \'nltk==3.8.1\',
        \'ollama==0.1.7\',
    ],
    entry_points={
        \'console_scripts\': [
            \'news-blink-backend=app:create_app\',
        ],
    },
    python_requires=\'>=3.9\',
)

