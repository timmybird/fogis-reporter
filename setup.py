"""Setup script for the fogis-reporter package."""

from setuptools import find_packages, setup

setup(
    name="fogis-reporter",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "fogis-api-client-timmyBird>=0.2.4",
        "requests>=2.31.0",
        "beautifulsoup4>=4.12.2",
        "tabulate>=0.9.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.4.0",
            "pytest-cov>=4.1.0",
            "pytest-mock>=3.10.0",
            "mypy>=1.5.1",
            "flake8>=6.1.0",
            "pre-commit>=3.5.0",
            "pexpect>=4.8.0",
            "pytest-console-scripts>=1.4.1",
        ],
    },
    entry_points={
        "console_scripts": [
            "fogis-reporter=fogis_reporter:main",
        ],
    },
    python_requires=">=3.8",
    description="A CLI application for reporting match events to the FOGIS system",
    author="Bartek Svaberg",
    author_email="bartek@example.com",
    url="https://github.com/PitchConnect/fogis-reporter",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
)
