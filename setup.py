from setuptools import setup, find_packages

setup(
    name="pylox",
    version="0.1.0",
    packages=find_packages(),
    entry_points={
        "console_scripts": [
            "pylox=pylox.__main__:main",
        ]
    },
)
