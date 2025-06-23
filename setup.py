#!/usr/bin/env python
# -*- coding: utf-8 -*-

# This setup.py file is provided for backward compatibility with older pip versions
# Modern Python packaging uses pyproject.toml (PEP 621)

from setuptools import setup

if __name__ == "__main__":
    try:
        setup()
    except Exception as e:
        print(f"Error during setup: {e}")
        print("This setup.py is provided for backward compatibility.")
        print("For modern Python packaging, use pyproject.toml with pip>=21.0.")