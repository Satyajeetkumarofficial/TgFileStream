import setuptools

from tgfilestream import __version__

try:
    long_desc = open("README.md").read()
except IOError:
    long_desc = "Failed to read README.md"

setuptools.setup(
    name="tgfilestream",
    version=__version__,
    url="https://mau.dev/tulir/tgfilestream",

    author="Tulir Asokan",
    author_email="tulir@maunium.net",

    description="A Telegram bot that can stream Telegram files to users over HTTP.",
    long_description=long_desc,
    long_description_content_type="text/markdown",

    packages=setuptools.find_packages(),

    install_requires=[
        "aiohttp>=3.9,<4",
        "telethon>=1.40,<2",
        "yarl>=1.9,<2",
    ],
    extras_require={
        "fast": ["cryptg>=0.4"],
    },
    python_requires=">=3.9",

    classifiers=[
        "Development Status :: 4 - Beta",
        "License :: OSI Approved :: GNU Affero General Public License v3 or later (AGPLv3+)",
        "Framework :: AsyncIO",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    entry_points="""
        [console_scripts]
        tgfilestream=tgfilestream.__main__:main_sync
    """,
)
