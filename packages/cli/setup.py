from setuptools import setup

setup(
    name="zta-cli",
    version="0.1.0",
    description="CLI Tool for ZeroTrust Agents Firewall",
    author="ZeroTrust Agents",
    py_modules=["zta"],
    install_requires=[
        "typer>=0.9.0",
        "requests>=2.25.0",
        "rich>=10.0.0",
    ],
    entry_points={
        "console_scripts": [
            "zta=zta:app",
        ],
    },
    python_requires=">=3.8",
)
