from setuptools import setup, find_packages

setup(
    name="agent-firewall",
    version="0.1.0",
    description="Python SDK for ZeroTrust Agents Firewall",
    author="ZeroTrust Agents",
    packages=find_packages(),
    install_requires=[
        "requests>=2.25.0",
    ],
    python_requires=">=3.8",
)
