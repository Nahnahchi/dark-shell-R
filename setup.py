from setuptools import setup, find_packages

pkg_vars = {}

with open("_version.py") as fp:
    exec(fp.read(), pkg_vars)

setup(
    name='DarkShell-R',
    version=pkg_vars['__version__'],
    packages=find_packages(),
    url='https://github.com/Nahnahchi/dark-shell-R',
    license='GPL-3.0',
    author='Nahnahchi',
    author_email='nahnahchi@gmail.com',
    description='An interactive shell for testing and debugging DARK SOULS REMASTERED',
    python_requires="==3.7",
    install_requires=[
        "prompt-toolkit>=3.0.0", "pythonnet", "PyGithub", "packaging", "colorama"
    ],
    dependency_links=[
        "https://github.com/prompt-toolkit/python-prompt-toolkit/tarball/master#egg=prompt-toolkit-3.0.5"
    ]
)
