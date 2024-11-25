from setuptools import setup, find_packages

# Read requirements from the file
with open("requirements.txt") as f:
    requirements = f.read().splitlines()

setup(
    name="sec-insights", 
    version="0.1", 
    description="A tool for processing SEC filings and generating insights.",
    url="https://github.com/mallikm99/sec-insights.git", 
    packages=find_packages(),
    install_requires=requirements,
    classifiers=[ 
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    entry_points={ 
        'console_scripts': [
            'sec-insights=sec_insights.src.pull:main', 
        ],
    },
)
