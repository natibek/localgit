import io

import setuptools

__version__ = "0.0.1"

description = "local_gits is a tool for managing local github repos."

long_description = io.open("README.md", encoding="utf-8").read()

setuptools.setup(
    name="local_gits",
    version=__version__,
    url="https://github.com/natibek/local_gits/tree/main",
    author="Nathnael Bekele",
    author_email="nwtbekele@gmail.com",
    python_requires=(">=3.11.0"),
    license="Apache 2.0",
    description=description,
    long_description=long_description,
    packages=["src"],
    entry_points={
        "console_scripts": [
            "local_gits=src.local_gits:main",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "License :: OSI Approved :: Apache 2.0",
        "Programming Language :: Python",
        "Operating System :: OS Independent",
    ],
)
