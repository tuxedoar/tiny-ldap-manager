# Copyright 2020 by Tuxedoar <tuxedoar@gmail.com>

# LICENSE

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

""" CSV handling helper functions for tiny-ldap-manager """

from sys import exit
from ast import literal_eval
import logging
import csv

def read_csv(csv_file):
    """ Read entries from CSV file """
    entries = []
    try:
        logging.info("\nOpening CSV file: %s\n\n", csv_file)
        with open(csv_file, 'r') as f:
            # csv.DictReader() returns an OrederedDict object
            csv_reader = csv.DictReader(f, delimiter=';')
            for entry in csv_reader:
                # Convert it to a normal dict!
                entry = dict(entry)
                entries.append(entry)
        return entries
    except IOError:
        logging.critical("Can't read %s file. Make sure it exist!\n", csv_file)
        exit(0)


def check_csv_literals(element):
    """ Recognize non-str Python objects when reading from CSV """
    # It seems that, when reading from a CSV file, Python treats everything as
    # string. This is a workaround so that it treats native Python objects as
    # such. This is mainly aimed at Python lists, since some LDAP attributes,
    # can have more than one value (ie: 'objectCLass')!. 
    try:
        element = literal_eval(element)
    except(SyntaxError, ValueError):
        pass
    return element


def process_each_csv_entry(csv_entry):
    """ Process each CSV entry """
    # Each csv_entry is a dict, which contains the attributes of each LDAP
    # entry to be added, PLUS, the DN!. The 'ldapdata' list, stores the dn and
    # the attributes as separate elements inside a tuple.
    ldapdata = []
    entry_dn = csv_entry['dn']
    # Since we don't want the dn as part of the attributes, let's remove it
    if 'dn' in csv_entry:
        del csv_entry['dn']

    for key, value in csv_entry.items():
        value = check_csv_literals(value)
        # Since we can have a Python list inside a CSV entry, we want to keep
        # it as it is. However, if it's not a list, we convert each element to
        # be one! (this is later required for the 'add_s' method of python-ldap).
        if isinstance(value, list):
            # Encode each element to a byte str if a list object is found.
            value = [i.encode('utf-8') for i in value]
            csv_entry[key] = value
        else:
            # Convert the attribute's value to a byte string!
            value = value.encode('utf-8')
            csv_entry[key] = [value]

    ldapdata.append((entry_dn, csv_entry))
    return ldapdata


def sanitize_csv_entry(csv_entry):
    """ Check for incomplete or wrong formatted CSV content

    Argument: csv_entry (a dict representing the content of each CSV entry)

    Function used by: bulk --modify-attributes
    """
    # A sanity check is performed on each CSV entry, each one being represented
    # as a dict, where: 'k' (key) is the DN and 'v' (value) is the attribute.
    # For each CSV entry, a True/False value is assigned as a result of having
    # checked both the DN and the attribute. This is stored in a tuple with the
    # result for both of them. Later, this is also used for establishing an
    # overall True/False result. 
    for k, v in csv_entry.items():
        # Both dn and attribute shouldn't have a 'None' or an empty string as
        # value. Otherwise, it means an incomplete CSV entry!.
        check_k = False if k == None or k == '' else True
        check_v = False if v == None or v == '' else True
        # Store a True/False result for DN and attribute
        result = (check_k, check_v)
    # Dict containing DN and attribute, should have 2 pairs of key-value.
    # This is an additional check to be sure there isn't an incomplete CSV
    # entry.
    if int(len(csv_entry)) < 2:
        result = (False, False)
    # If check's result for DN or attribute is False, we assume an overall
    # False result. 
    if False in result:
        result = False
    else:
        result = True
    return result


def csv_sanitizer(csv_file):
    """ Evaulate each CSV entry and adds a verification result of its content

    Function used by: bulk --modify-attributes
    """
    sanitized_csv = []
    csv_data = read_csv(csv_file)
    # Check it's not an empty file
    if csv_data:
        for each_entry in csv_data:
            # Store both the CSV entry and the sanity check result on a list.
            result = sanitize_csv_entry(each_entry)
            sanitized_csv.append((each_entry, result))
    else:
        logging.info("Empty file or wrong format: nothing to process!\n")
        exit(0)
    return sanitized_csv
