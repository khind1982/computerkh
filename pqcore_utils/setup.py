import setuptools

setuptools.setup(
    name="pqcoreutils",
    version="0.8.6",
    author="Daniel Bye",
    author_email="dan.bye@proquest.com",
    description="Basic Content handling functionality",
    packages=setuptools.find_packages(),
    install_requires=["dateparser", "lxml>=4.2", "tabulate", "colorama"],
    entry_points={
        "console_scripts": ["filebundler=pqcoreutils.cli:bundler_main"],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: Other/Proprietary License",
        "Operating System :: POSIX",
    ],
)
