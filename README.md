# Tiny LDAP Manager
This CLI tool allows you to easily perform basic operations (changes) on your
LDAP server. It's aimed to ease these kind of tasks, without having to, necessarily,
deal with *LDIF* files. Moreover, it permits you to do some of these things, in bulk!.

## Features
More precisely, this program, allows you to:
 * Modify LDAP attributes (*replace*, *add* and *delete* modes, are supported!).
 * Delete LDAP entries. 
 * Add LDAP entries with their corresponding *attributes*, by importing them
 from a CSV file!.
 * Query the LDAP attributes of a particular entry, based on its DN. 

For the time being, there some features that I've planned, that aren't yet
implemented. Hopefully, I'll do so in future releases!. 

## Requirements
This is what it needs, in order to work:
 * [Python 3](https://www.python.org/downloads/)
 * [python-ldap](https://pypi.python.org/pypi/python-ldap/) library (tested
with *v3.2.0*).

## Disclaimer
I don't take any responsibility on the consequences of the usage of this
program!. Use it at your own risk!!.

It's advisable to always have a working backup of your LDAP database, prior to
ANY modification!.

## Installation

## Usage

## License
This program is distributed under the GPLv3 license.
