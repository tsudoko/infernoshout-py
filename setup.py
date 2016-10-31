#!/usr/bin/env python3
from setuptools import setup

setup(
    name="infernoshout",
    version="0.1",
    license="Public Domain",
    packages=["infernoshout"],
    install_requires=[
        "beautifulsoup4",
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
