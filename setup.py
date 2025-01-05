from setuptools import setup

setup(
    name="tradesmart",
    version="0.0.2",
    author="ichimei0125",
    description="A cryptocurrency and stock trading bot with simulation support",
    # packages=find_packages(),
    install_requires=[
        "ccxt==4.4",
        "pandas==2.2",
        "numpy==2.2",
        "PyYAML",
        "pytest",
        "SQLAlchemy==2.0",
        "mariadb==1.1",
        "TA-Lib==0.6",
    ],
    # entry_points={
    #     "console_scripts": [
    #         "tradebot = scripts.tradebot_cli:main", 
    #     ],
    # },
    include_package_data=True,
    python_requires=">=3.12,<4",
)