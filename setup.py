from setuptools import setup, find_packages

pkg_vars = {}

with open("_version.py") as fp:
    exec(fp.read(), pkg_vars)

setup(
    name=pkg_vars["__app_name__"],
    version=pkg_vars["__version__"],
    packages=find_packages(),
    url=pkg_vars["__github__"],
    license='GPL-3.0',
    author=pkg_vars["__author__"],
    author_email=pkg_vars["__email__"],
    description=pkg_vars["__description__"],
    python_requires="==3.7",
    install_requires=[
        "prompt-toolkit>=3.0.0", "pythonnet", "PyGithub", "packaging", "colorama", "mttkinter", "beepy", "anyascii"
    ],
    dependency_links=[
        "https://github.com/prompt-toolkit/python-prompt-toolkit/tarball/master#egg=prompt-toolkit-3.0.5"
    ]
)
