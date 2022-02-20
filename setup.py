from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="zappaenv",
    version='0.1.0',
    author="Moshe Dicker",
    author_email='dickermoshe@gmail.com',
    description="A tool for running Zappa commands in a Lambda-like' environment.",
    url='https://github.com/dickermoshe/zappaenv',
    license='GNU General Public License v3.0',
    long_description=long_description,
    long_description_content_type="text/markdown",
    install_requires=[
        'Click',
        'docker'
    ],
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'zappaenv = zappaenv:zappaenv',
        ],
    },
    python_requires=">=3.6,!=3.10.*,!=3.11.*",
)