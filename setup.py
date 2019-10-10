from setuptools import setup, find_packages

setup(
    name='dark-shell-R',
    version='1.0',
    packages=find_packages(),
    url='https://github.com/Nahnahchi/dark-shell-R',
    license='GPL-3.0',
    author='Nahnahchi',
    author_email='sawalozb@gmail.com',
    description='A command line tool for testing and debugging DARK SOULS REMASTERED',
    python_requires=">=3.7",
    install_requires=[
        "prompt-toolkit>=3.0.0"
    ],
    dependency_links=[
        "https://github.com/prompt-toolkit/python-prompt-toolkit/tarball/master#egg=prompt-toolkit-3.0.0"
    ]
)
