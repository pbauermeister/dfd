"""A setuptools based setup module.

See:
https://packaging.python.org/guides/distributing-packages-using-setuptools/
"""

from setuptools import setup, find_packages
import pathlib

with open('VERSION', encoding='utf-8') as f:
    VERSION = f.read().strip()

here = pathlib.Path(__file__).parent.resolve()
long_description = (here / "README.md").read_text(encoding="utf-8")

setup(
    name="data-flow-diagram",
    version=VERSION,
    description="Commandline tool to generate data flow diagrams from text",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/pbauermeister/dfd",
    author="Pascal Bauermeister",
    author_email="pascal.bauermeister@gmail.com",
    classifiers=[
        # https://pypi.org/classifiers/ :
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Information Technology",
        "Topic :: Software Development",
        "Topic :: Software Development :: Documentation",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Programming Language :: Python :: 3",
    ],
    keywords="diagram-generator, development, tool",
    license="GNU General Public License v3 (GPLv3)",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    python_requires=">=3.10, <4",
    install_requires=["svgwrite", "svglib"],
    extras_require={
        "dev": ["check-manifest"],
        "test": ["coverage"],
    },
    package_data={
#        "data_flow_diagram": ["tbdpackage__data.dat"],
    },
#    data_files=[('data_flow_diagram', ["VERSION"])],
    # The following would provide a command called `data-flow-diagram` which
    # executes the function `main` from this package when invoked:
    entry_points={
        "console_scripts": [
            "data-flow-diagram=data_flow_diagram:main",
        ],
    },
    project_urls={
        "Bug Reports": "https://github.com/pbauermeister/dfd/issues",
#        "Funding": "https://donate.pypi.org",
#        "Say Thanks!": "http://saythanks.io/to/example",
        "Source": "https://github.com/pbauermeister/dfd",
    },
)
