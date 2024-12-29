from setuptools import setup, find_packages

setup(
    name="tradesmart",
    version="0.1.0",
    author="ichimei0125",
    description="A cryptocurrency and stock trading bot with simulation support",
    packages=find_packages(),
    install_requires=[
        "ccxt",
        "pandas",
        "numpy",
        "PyYAML",
        "pytest",
    ],
    # entry_points={
    #     "console_scripts": [
    #         "tradebot = scripts.tradebot_cli:main", 
    #     ],
    # },
    include_package_data=True,
    python_requires=">=3.12,<4",
)