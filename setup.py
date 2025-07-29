#!/usr/bin/env python3
from setuptools import find_packages, setup

setup(
    name="localLLM-client",
    version="0.1.0",
    description="Python SDK for localLLM QA Inference API",
    packages=find_packages(),
    install_requires=[
        "requests",
        "pydantic",
    ],
    entry_points={
        "console_scripts": [
            "localllm-client=localllm_client.client:main",
        ],
    },
    author="",
    license="",
)
