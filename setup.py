#!/usr/bin/env python3
from setuptools import setup

setup(
    name="infernoshout",
    version="0.2",
    license="Public Domain",
    packages=["infernoshout"],
    install_requires=[
        "beautifulsoup4",
        "dateparser",
        "requests",
        "setproctitle",
    ],
    scripts=["inferno-cli"],
    classifiers=[
        "License :: Public Domain",
        "Programming Language :: Python :: 3 :: Only",
        "Topic :: Communications :: Chat",
        "Topic :: Utilities",
    ]
)
