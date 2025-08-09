"""
Setup file for The Dojo - Office Space Allocation.
"""
from setuptools import setup, find_packages

setup(
    name="the_dojo",
    version="1.0.0",
    packages=find_packages('src'),
    package_dir={'': 'src'},
    install_requires=[
        'docopt>=0.6.2',
    ],
    entry_points={
        'console_scripts': [
            'dojo=cli:main',
        ],
    },
    author="Your Name",
    author_email="your.email@example.com",
    description="The Dojo - Office Space Allocation System",
    long_description=open('README.md').read(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/the-dojo",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.8',
)
