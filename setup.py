from setuptools import setup, find_namespace_packages

with open("README.md") as f:
    long_description = f.read()

setup(
    name="flyttdata",
    author="Pontus Höjer",
    url="https://github.com/pontushojer/flyttdata/",
    description="Flyttdata",
    long_description=long_description,
    long_description_content_type="text/markdown",
    license="MIT",
    python_requires=">=3.6",
    package_dir={"": "src"},
    packages=find_namespace_packages("src"),
    entry_points={"console_scripts": ["flyttdata = flyttdata.__main__:main"]},
    classifiers=[
        "Development Status :: 4 - Beta",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
    ]
)