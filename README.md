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

At present, there are some features that I've planned, that aren't yet
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
To start with, here's the help output:
```
usage: tiny-ldap-manager.py [-h] SERVER BINDDN {ls,modify,add,delete} ...

Easily perform several LDAP operations

positional arguments:
  SERVER                URI formatted address of the LDAP server
  BINDDN                DN of the user to bind the LDAP server
  {ls,modify,add,delete}
    ls                  List LDAP attributes for specified DN
    modify              Modify an LDAP attribute
    add                 Add LDAP entries from a CSV file
    delete              Delete an LDAP entry

optional arguments:
  -h, --help            show this help message and exit

```
### Basic syntax
The basic syntax you've to respect is the following:
```
tiny-ldap-manager [SERVER] [BINDDN] [ACTION] [ARGUMENTS]
```
In order of appereance:
 * `[SERVER]` belongs to the URI formatted address of your LDAP server. This
 argumentis mandatory!.
 * `[BINDDN]` is the *DN* (*"Distinguished Name"*) of the LDAP user with
 permissions for the operation you wish to perform!. It's a mandatory argument!.
 * `[ACTION]` is the actual operation you want to perform. At present, there
 are four valid operations you can use: `ls`, `modify`, `add` or `delete`. This
 argument is also mandatory and you must provide ONLY one of them!. Please, see
 below for more details.
 * `[ARGUMENTS]`: when you perform an *ACTION*, any of them requires, at least, one
 or more additional arguments. You can add the `--help` argument to any of
 them, for specific details. Please, see below for more on this.

## License
This program is distributed under the GPLv3 license.
