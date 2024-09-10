import setuptools

from src._version import __version__

description = "localgit is a tool for managing local git repo clones."

setuptools.setup(
    name="localgit",
    version=__version__,
    url="https://github.com/natibek/localgit/tree/main",
    author="Nathnael Bekele",
    author_email="nwtbekele@gmail.com",
    python_requires=(">=3.11.0"),
    license="Apache 2.0",
    description=description,
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    packages=["src"],
    entry_points={
        "console_scripts": [
            "localgit=src.localgit:main",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
)
