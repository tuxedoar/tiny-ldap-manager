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
The recommended way to install this program, is by using `pip`:
```
pip install tiny-ldap-manager
```

## Usage
To start with, here's the help output:
```
usage: tiny-ldap-manager [-h] [-v] SERVER BINDDN {ls,modify,add,delete} ...

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
  -v, --version         Show current version
```
### Basic syntax
The basic syntax you've to respect is the following:
```
tiny-ldap-manager [SERVER] [BINDDN] [ACTION] [ARGUMENTS]
```
In order of appearance:
 * `[SERVER]` belongs to the *URI formatted address* of your LDAP server. This
 argument is mandatory!.
 * `[BINDDN]` is the *DN* (*"Distinguished Name"*) of the LDAP user with
 permissions for the operation you wish to perform!. It's a mandatory argument!.
 * `[ACTION]` is the actual operation you want to perform. At present, there
 are four valid operations you can use: `ls`, `modify`, `add` or `delete`. This
 argument is also mandatory and you must provide ONLY one of them!. Please, see
 below for more details.
 * `[ARGUMENTS]`: when you perform an `[ACTION]`, any of them requires, at least, one
 or more additional arguments. You can add the `--help` argument to any of
 them, for specific details. Please, see below for more on this.

### Performing different LDAP operations

#### Authentication
Take into account that, an *authenticated session* is always assumed. So you are
gonna be asked for the corresponding credentials, each time you perform an
operation!.

#### Listing attributes of an LDAP entry
The `ls` action, allows you to quickly see the attributes of a particular LDAP
entry. For this, you have to provide the DN of the latter. For example:
```
tiny-ldap-manager ldap://192.168.100.5 "cn=config" ls "uid=joe,ou=people,dc=somecorp,dc=com"
```

#### Modifying an attribute of an LDAP entry
For modifying or adding an attribute to an LDAP entry, you logically use the
`modify` action. There are three types of modifications possible to use:
 * `REPLACE` is to be used whenever you want to modify the value of an existing
 attribute. This is the mode **used by default**!.
 * `ADD` is for adding a non-existing attribute!.
 * `DELETE` is, of course, for deleting an existing attribute!. 

##### REPLACE mode
If you don't provide any additional arguments, the `REPLACE` mode is used by
default!. The complete syntax for it, is:
```
tiny-ldap-manager [SERVER] [USERDN] modify [ATTRIBUTE] [VALUE] 
```
Where `[ATTRIBUTE]` is the name of the *attribute* you want to modify, and
`[VALUE]` is the *new value* for that *attribute*!.

Let's see an example:
```
tiny-ldap-manager ldap://192.168.100.5 "cn=config" modify "uid=joe,ou=people,dc=somecorp,dc=com" telephoneNumber "5555" 
```
Above, we're modifying the existing `telephoneNumber` attribute with a new value
of`5555`.

Make sure that the new value for the attribute you're modifying, is NOT the
same as its current value!. Otherwise, you'll get an error!.

##### ADD mode
In order to use a different mode for making a modification, you've to do it
using the `-M` argument, as follows: 
```
tiny-ldap-manager ldap://192.168.100.5 "cn=config" modify -M ADD "uid=willy,ou=people,dc=somecorp,dc=com" telephoneNumber "8006666"
```
With this latter example, we add the `telephoneNumber` attribute, with its
corresponding value. 

It's important to note that this program is *case-sensitive*, so the
*modification mode* always goes with capital letters!.

##### DELETE mode
Finally, an example for using the `DELETE` mode, for removing an existing LDAP attribute:
```
tiny-ldap-manager ldap://192.168.100.5 "cn=config" modify -M DELETE "uid=charles,ou=people,dc=somecorp,dc=com" telephoneNumber ""
```
Note that the *double quotes* at the end of the command, **are necessary!**.

#### Adding entries to your LDAP
The way to add entries to an LDAP database with `tiny-ldap-manager`, is by
creating a CSV file using the header row (first row), to specify the attributes
for each new entry. You must ensure that you use a *semi-colon* as the CSV
delimiter!.

Besides the CSV *header row*, the rest of them, are to be used to define the
value of each corresponding attribute.

The order in which the LDAP attributes are specified in the CSV file, is not
important, as long as there is a logical correlation between the *value* assigned
to each *attribute* and the *attribute* itself!. Even then, for the sake of
clarity, it's a good idea to always put the DN in the first place!.

Now, let's see an example of a CSV file content:
```
dn;objectClass;uid;cn;sn;givenName;displayName;mail
uid=cdarwin,ou=people,dc=scileague,dc=org;['inetOrgPerson','organizationalPerson'];cdarwin;cdarwin;Darwin;Charles;Charles Darwin;charlesdarwin@scileague.org
uid=alovelace,ou=people,dc=scileague,dc=org;inetOrgPerson;alovelace;alovelace;Lovelace;Ada;Ada Lovelace;adalovelace@scileague.org
uid=aeinstein,ou=people,dc=scileague,dc=org;inetOrgPerson;aeinstein;aeinstein;Einstein;Albert;Albert Einstein;alberteinstein@scileague.org
```
The following is how you would import such entries:
```
tiny-ldap-manager ldap://192.168.100.5 "cn=config" add scileague.csv
```

As you might noticed in the CSV, the entry that belongs to *Charles Darwin*, has
a *formatted list* of *values* for the `objectClass` *attribute*. That's a
supported way to include more than one *value* for a given *attribute*.

As a final note about importing new LDAP entries, if one or many of them, already
exist in the LDAP database, you can be sure that they won't be imported, but 
equally important, is the fact that they won't interrupt the whole process
neither. An output message is shown in each case.    

#### Deleting an entry from your LDAP
You can simply remove an LDAP entry from your database, by indicating its DN,
as is shown next:
```
tiny-ldap-manager ldap://192.168.100.5 "cn=config" delete "uid=bob,ou=people,dc=somecorp,dc=com"
```
Poor Bob!. :)

## License
This software is distributed under the GPLv3 license.
