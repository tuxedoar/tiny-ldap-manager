from setuptools import setup

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='tiny-ldap-manager',
    version='0.1.1',
    description='Easily perform several LDAP operations',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='https://github.com/tuxedoar/tiny-ldap-manager',
    author='tuxedoar',
    author_email='tuxedoar@gmail.com',
    license='GPLv3'
    packages=['tiny_ldap_manager'],
    python_requires='>=3.6',
    scripts=["tiny_ldap_manager/_version.py"],
    entry_points={
        "console_scripts": [
        "tiny-ldap-manager = tiny_ldap_manager.tiny_ldap_manager:main",
        ],
    },
    install_requires=[
    'python-ldap'
    ],

    classifiers=[
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.6",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
        "Intended Audience :: System Administrators",
        "Environment :: Console",
        "Topic :: System :: Systems Administration :: Authentication/Directory :: LDAP",
        ],
)
