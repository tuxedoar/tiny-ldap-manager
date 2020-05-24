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

import argparse
import logging
import getpass
from sys import exit
import csv
from ast import literal_eval
import ldap
import ldap.modlist as modlist

def main():
    """ Menu arguments handling """
    # Setup logging
    logging.basicConfig(format='%(message)s', level=logging.INFO)

    parser = argparse.ArgumentParser(
        description="Easily perform several LDAP operations")
    parser.add_argument('SERVER', help='URI formatted address of the LDAP server')
    parser.add_argument('BINDDN', help='DN of the user to bind the LDAP server')
    # LDAP subparser for operations available to perform
    subparser = parser.add_subparsers(dest='action')
    # List LDAP attributes from DN!
    ldap_ls = subparser.add_parser('ls', \
            help='List LDAP attributes for specified DN')
    ldap_ls.add_argument('basedn')
    # Modify existing LDAP attributes
    ldap_modify = subparser.add_parser('modify', \
            help="Modify an LDAP attribute")
    ldap_modify.add_argument('modify_dn', help="Object DN to be modified")
    ldap_modify.add_argument('target_attr', help="Attribute to be modified")
    ldap_modify.add_argument('new_value', help="New value for attribute")
    ldap_modify.add_argument('-M', '--modifymode', nargs='?', type=str, \
            default='REPLACE', \
            help="Change operation mode for modifying an attribute")
    # Add LDAP entries from a CSV file!
    ldap_add_entry = subparser.add_parser('add', help="Add LDAP entries from a " \
    "CSV file")
    ldap_add_entry.add_argument('csvfile', \
            help='CSV file to import LDAP entries from')
    # Delete an LDAP entry!
    ldap_delete = subparser.add_parser('delete', help="Delete an LDAP entry")
    ldap_delete.add_argument("delete_dn", help="DN of the entry to be removed")

    args = parser.parse_args()

    try:
        #if args.action != None:
        if args.action == "ls":
            ldap_session = start_ldap_session(args.SERVER, args.BINDDN)
            ldap_ls.set_defaults(func=ldap_action_ls(ldap_session, args.basedn))
        elif args.action == "add":
            ldap_session = start_ldap_session(args.SERVER, args.BINDDN)
            ldap_add_entry.set_defaults(func=ldap_action_add_entry(ldap_session, args.csvfile))
        elif args.action == "modify":
            ldap_session = start_ldap_session(args.SERVER, args.BINDDN)
            ldap_modify.set_defaults(func=ldap_action_modify(ldap_session, \
                args.modify_dn, args.target_attr, args.new_value, \
                args.modifymode))
        elif args.action == "delete":
            ldap_session = start_ldap_session(args.SERVER, args.BINDDN)
            ldap_delete.set_defaults(func=ldap_action_delete(ldap_session, \
                args.delete_dn))
        else:
            logging.critical("You need to provide at least one action to perform!")
            exit(0)
    except (KeyboardInterrupt, ldap.SERVER_DOWN, ldap.UNWILLING_TO_PERFORM, \
            ldap.INVALID_CREDENTIALS, ldap.INVALID_DN_SYNTAX, \
            ldap.NO_SUCH_OBJECT) as e:
            exit(e)


def start_ldap_session(server, binddn):
    """ Initiate the LDAP session  """
    ldap.set_option(ldap.OPT_X_TLS_REQUIRE_CERT, ldap.OPT_X_TLS_NEVER)
    ldap.set_option(ldap.OPT_PROTOCOL_VERSION, ldap.VERSION3)
    l = ldap.initialize(server, bytes_mode=False)
    l.set_option(ldap.OPT_REFERRALS, 0)

    creds = getpass.getpass('\nPlease, enter LDAP credentials for {}: '.format(binddn))
    lsession = l.simple_bind_s(binddn, creds)
    if lsession:
        logging.info("\nSuccessful LDAP authentication!\n")
    return l


def ldap_action_ls(ldap_session, basedn):
    """ Show attributes for specified DN """
    logging.info("\nShowing  attributes for %s:\n\n", basedn)
    attrs = retrieve_attrs_from_dn(ldap_session, basedn)
    for key, value in attrs[0].items():
        print("{}:\t{}".format(key, value[0].decode()))
    ldap_session.unbind()


def retrieve_attrs_from_dn(ldap_session, basedn):
    """ Retrieve attributes from given DN """
    ldap_data = ldap_session.search_s(basedn, ldap.SCOPE_BASE, 'objectClass=*')
    attrs = [i[1] for i in ldap_data]
    return attrs


def ldap_modify_replace_mode(ldap_session, attrs, attr, dn, new_value):
    """ Replace an existing LDAP attribute's value """
    # Do the actual operation!
    current_attr = attrs[0][attr]
    old = {attr:current_attr}
    new = {attr:new_value}
    ldif = modlist.modifyModlist(old,new)
    ldap_session.modify_s(dn, ldif)
    logging.info("\nAttribute %s value has been changed:\n\n" \
    " Previous value: %s\n New value: %s\n" \
    , attr, current_attr[0].decode(), new_value[0].decode())


def ldap_modify_add_mode(ldap_session, dn, attr, value):
    """ Add attribute in LDAP entry if NOT exists  """
    new_attr = [(ldap.MOD_ADD, attr, value)]
    ldap_session.modify_s(dn, new_attr)
    logging.info("A new attribute has been added:\n\n %s: %s\n", \
                attr, value[0].decode())


def ask_user_confirmation():
    """ Ask for user confirmation """
    user_confirm = str(input("Are you sure you wanna proceed? (YES/n)"))
    while user_confirm != "YES" and user_confirm != "n":
        user_confirm = str(input("Not a valid answer!. Proceed? (YES/n)"))
    if user_confirm == 'n':
        logging.info("\nOperation has been canceled!!\n")
        user_confirm = False
    else:
        user_confirm = True
    return user_confirm


def ldap_modify_delete_mode(ldap_session, dn, attr):
    """ Delete an attribute from LDAP entry """
    logging.info("The following attribute from %s will be removed:\n\n%s\n", dn, attr)
    if ask_user_confirmation():
        ldap_session.modify_s(dn, [(ldap.MOD_DELETE, attr, None)])
        logging.info("\nLDAP attribute %s has been removed!!\n", attr)


def ldap_action_modify(ldap_session, dn, attr, new_value, add_mode):
    """ Modify LDAP attributes """
    logging.info("\nPerforming an attribute modification in %s!\n", dn)
    attrs = retrieve_attrs_from_dn(ldap_session, dn)
    # Encode attribute's new value to byte strings 
    new_value = [new_value.encode('utf-8')]

    # Valid modify modes are: REPLACE, ADD, DELETE
    # Check existing attr value != new value!
    if add_mode == 'REPLACE' and \
        attrs[0].get(attr) and \
        attrs[0][attr][0].decode() == new_value[0].decode():
        logging.critical("\nERROR: Existing value for attribute %s and the " \
        "provided one, can't be the same!\n", attr)
    # Modify the existing attribute
    elif add_mode == 'REPLACE' and attrs[0].get(attr):
        ldap_modify_replace_mode(ldap_session, attrs, attr, dn, new_value)
    # Create the given attribute if ADD mode is set! 
    elif add_mode == 'ADD' and not attrs[0].get(attr):
        ldap_modify_add_mode(ldap_session, dn, attr, new_value)
    elif add_mode == 'DELETE' and attrs[0].get(attr):
        ldap_modify_delete_mode(ldap_session, dn, attr)
    else:
        logging.critical("\nERROR: Invalid modify mode or conflict exists " \
        "in DN %s with attribute %s!.\n Please, verify and try again!\n", \
        dn, attr)
    logging.info("\n\nClosing connection!\n")
    ldap_session.unbind()


def ldap_action_delete(ldap_session, delete_dn):
    """ Delete an LDAP entry based on DN """
    logging.info("\nWARNING: you are about to delete the " \
    "following LDAP entry:\n\n %s\n", delete_dn)
    logging.info("\n##### This operation IS NOT REVERSIBLE!!!. " \
    "ALWAYS have a working backup first! #####\n")
    if ask_user_confirmation():
        ldap_session.delete_s(delete_dn)
        logging.info("\nLDAP entry %s has been removed!!\n", delete_dn)
    logging.info("\n\nClosing connection!\n")
    ldap_session.unbind()


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


def read_csv(csv_file):
    """ Read entries from CSV file """
    entries = []
    try:
        logging.info("Opening CSV file: %s\n\n", csv_file)
        with open(csv_file, 'r') as f:
            # csv.DictReader() returns an OrederedDict object
            csv_reader = csv.DictReader(f, delimiter=';')
            for entry in csv_reader:
                each_entry = {}
                # Convert it to a normal dict!
                entry = dict(entry)
                entries.append(entry)
        return entries
    except IOError:
        logging.critical("Can't read %s file. Make sure it exist!\n", csv_file)
        exit(0)


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
        # Convert the attribute's value to a byte string! 
        value = value.encode('utf-8')
        # Since we can have a Python list inside a CSV entry, we want to keep
        # it as it is. However, if it's not a list, we convert each element to
        # be one! (this is later required for the 'add_s' method of python-ldap). 
        if isinstance(value, list):
            csv_entry[key] = value
        else:
            csv_entry[key] = [value]

    ldapdata.append((entry_dn, csv_entry))
    return ldapdata


def ldap_action_add_entry(ldap_session, csv_file):
    "Add LDAP entries from CSV"
    csv_entries = read_csv(csv_file)

    ldapdata = [process_each_csv_entry(i) for i in csv_entries]
    for content in ldapdata:
        dn = content[0][0]
        attributes = content[0][1]
        ldif = modlist.addModlist(attributes)
        try:
            ldap_session.add_s(dn,ldif)
            logging.info("Adding LDAP entry: %s", dn)
        except ldap.ALREADY_EXISTS:
            logging.warning("Failed to add entry: %s. Already exists!", dn)
    logging.info("\n\nClosing connection!\n")
    ldap_session.unbind()


if __name__ == "__main__":
    main()
