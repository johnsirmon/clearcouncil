"""Setup script for ClearCouncil."""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="clearcouncil",
    version="1.0.0",
    author="ClearCouncil Contributors",
    author_email="support@clearcouncil.org",
    description="Local Government Transparency Tool using RAG - Dual Licensed",
    long_description=long_description,
    long_description_content_type="text/markdown",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Education",
        "License :: Other/Proprietary License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Education",
        "Topic :: Office/Business :: Financial :: Accounting",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "clearcouncil=clearcouncil.cli.main:main",
        ],
    },
    include_package_data=True,
    package_data={
        "clearcouncil": ["config/councils/*.yaml"],
    },
    license="Dual License: MIT (Personal/Educational), Commercial License Required (Commercial/Governmental/Organizational)",
    url="https://github.com/yourusername/clearcouncil",
    project_urls={
        "Bug Tracker": "https://github.com/yourusername/clearcouncil/issues",
        "Documentation": "https://github.com/yourusername/clearcouncil/blob/main/README.md",
        "Commercial License": "mailto:support@clearcouncil.org",
    },
)