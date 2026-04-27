from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="marin-AI",
    version="1.0.0",
    author="Bayazid Habib Siddikee",
    author_email="2208053.mte.ruet@gmail.com",
    description="A romantic AI chatbot featuring Marin Kitagawa persona with TTS capabilities",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/BayazidHabibSiddikee/Marin-Kitagawa-Himels-GF.git",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: RUET License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.14",
        ],
    python_requires=">=3.8",
    install_requires=[
        "Flask>=2.0.0",
        "requests>=2.25.0",
        "Werkzeug>=2.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=6.0",
            "black>=21.0",
            "flake8>=3.8",
        ],
    },
    entry_points={
        "console_scripts": [
            "marin-chat=app:app",
        ],
    },
    include_package_data=True,
)
