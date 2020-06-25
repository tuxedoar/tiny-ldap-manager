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

from sys import exit
import argparse
import logging
import ldap
import ldap.modlist as modlist
from _version import __version__
from tiny_ldap_manager.tlmgr_core import start_ldap_session
from tiny_ldap_manager.tlmgr_core import retrieve_attrs_from_dn
from tiny_ldap_manager.tlmgr_core import ask_user_confirmation
from tiny_ldap_manager.tlmgr_core import ldap_delete_single_dn
from tiny_ldap_manager.delete_bulk import ldap_delete_bulk
from tiny_ldap_manager.tlmgr_modify import ldap_replace_attr
from tiny_ldap_manager.tlmgr_modify import ldap_add_attr
from tiny_ldap_manager.tlmgr_modify import ldap_delete_attr
from tiny_ldap_manager.tlmgr_modify import ldap_modify_bulk
from tiny_ldap_manager.tlmgr_csv import read_csv
from tiny_ldap_manager.tlmgr_csv import process_each_csv_entry


def main():
    """ Process user's arguments """
    # Setup logging
    logging.basicConfig(format='%(message)s', level=logging.INFO)

    menu = menu_handler()
    args = menu[0]
    # Invoke sub-commands in argparse
    ldap_ls = menu[1].choices['ls']
    ldap_add_entry = menu[1].choices['add']
    ldap_modify = menu[1].choices['modify']
    ldap_delete = menu[1].choices['delete']
    ldap_bulk = menu[1].choices['bulk']

    try:
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
        elif args.action == "bulk":
            ldap_session = start_ldap_session(args.SERVER, args.BINDDN)
            ldap_bulk.set_defaults(func=ldap_action_bulk(ldap_session, \
                args))
        else:
            logging.critical("You need to provide at least one action to perform!")
            exit(0)
    except (KeyboardInterrupt, ldap.SERVER_DOWN, ldap.UNWILLING_TO_PERFORM, \
            ldap.INVALID_CREDENTIALS, ldap.INVALID_DN_SYNTAX, \
        ldap.NO_SUCH_OBJECT) as e:
        exit(e)


def menu_handler():
    """ Menu arguments handling """
    parser = argparse.ArgumentParser(
        description="Easily perform several LDAP operations")
    parser.add_argument('SERVER', help='URI formatted address of the LDAP server')
    parser.add_argument('BINDDN', help='DN of the user to bind the LDAP server')
    parser.add_argument('-v', '--version', action='version', \
    version="%(prog)s {version}".format(version=__version__), \
    help='Show current version')
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
    # Usage of argparse's mutually exclusive group for LDAP operations in bulk!
    bulk = subparser.add_parser('bulk', help='Perform an LDAP operation in bulk')
    gbulk = bulk.add_mutually_exclusive_group(required=True)
    # Modify LDAP attributes in bulk
    gbulk.add_argument('--modify-attributes')
    # Delete LDAP entries in bulk
    gbulk.add_argument('--delete-entries')

    args = parser.parse_args()
    return args, subparser


def ldap_action_ls(ldap_session, basedn):
    """ Show attributes for specified DN """
    logging.info("\nShowing  attributes for %s:\n\n", basedn)
    attrs = retrieve_attrs_from_dn(ldap_session, basedn)
    logging.info("ATTRIBUTE\t\t\t\t\tVALUE\n")
    for key, value in attrs[0].items():
        # Deal with attributes with multiple values!
        if len(value) > 1:
            for v in value:
                print("{:<40} :\t{}".format(key, v.decode()))
        else:
            print("{:<40} :\t{}".format(key, value[0].decode()))
    ldap_session.unbind()


def ldap_action_modify(ldap_session, dn, attr, new_value, add_mode):
    """ Modify LDAP attributes """

    logging.info("\nPerforming an attribute modification in %s!\n", dn)
    attrs = retrieve_attrs_from_dn(ldap_session, dn)
    # Encode attribute's new value to byte strings
    new_value = [new_value.encode('utf-8')]
    current_attr_exists = attrs[0].get(attr)
    new_attr_value = new_value[0].decode()

    # Valid modify modes are: REPLACE, ADD, DELETE
    if add_mode == 'REPLACE' and current_attr_exists:
        current_attr_value = attrs[0][attr][0].decode()
        # Check existing attr value != new value!
        if current_attr_value == new_attr_value:
            logging.critical("\nERROR: Existing value for attribute %s and the " \
            "new one, can't be the same!\n", attr)
        else:
            # Modify the existing attribute
            ldap_replace_attr(ldap_session, attrs, attr, dn, new_value)
    # Create the given attribute if ADD mode is set!
    elif add_mode == 'ADD' and not current_attr_exists:
        ldap_add_attr(ldap_session, dn, attr, new_value)
    elif add_mode == 'DELETE' and current_attr_exists:
        ldap_delete_attr(ldap_session, dn, attr)
    else:
        logging.critical("\nERROR: Invalid modify mode or conflict exists " \
        "in DN %s with attribute %s!.\n Please, verify and try again!\n", \
        dn, attr)
    logging.info("\n\nClosing connection!\n")
    ldap_session.unbind()


def ldap_action_delete(ldap_session, delete_dn):
    """ Delete an LDAP entry """
    logging.info("\n##### Please, remember to have a working BACKUP of your " \
    "LDAP database, prior to ANY modification!! #####\n")
    ldap_delete_single_dn(ldap_session, delete_dn)
    logging.info("\n\nClosing connection!\n")
    ldap_session.unbind()


def ldap_action_add_entry(ldap_session, csv_file):
    "Add LDAP entries from CSV"
    csv_entries = read_csv(csv_file)

    ldapdata = [process_each_csv_entry(i) for i in csv_entries]
    for content in ldapdata:
        dn = content[0][0]
        attributes = content[0][1]
        ldif = modlist.addModlist(attributes)

        try:
            ldap_session.add_s(dn, ldif)
            logging.info("Adding LDAP entry: %s", dn)
        except ldap.ALREADY_EXISTS:
            logging.warning("Failed to add LDAP entry: %s. Already exists!", dn)
    logging.info("\n\nClosing connection!\n")
    ldap_session.unbind()


def ldap_action_bulk(ldap_session, bulk_action):
    """ Perform an LDAP operation in bulk """
    args = bulk_action
    if args.modify_attributes:
        csv_file = args.modify_attributes
        ldap_modify_bulk(ldap_session, csv_file)
    elif args.delete_entries:
        txt_file=args.delete_entries
        ldap_delete_bulk(ldap_session, txt_file)
    logging.info("\n\nClosing connection!\n")
    ldap_session.unbind()


if __name__ == "__main__":
    main()
