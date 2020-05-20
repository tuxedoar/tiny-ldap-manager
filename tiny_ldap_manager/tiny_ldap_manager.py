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
    # Delete an LDAP entry!
    ldap_delete = subparser.add_parser('delete', help="Delete an LDAP entry")
    ldap_delete.add_argument("delete_dn", help="DN of the entry to be removed")

    args = parser.parse_args()

    try:
        #if args.action != None:
        if args.action == "ls":
            ldap_session = start_ldap_session(args.SERVER, args.BINDDN)
            ldap_ls.set_defaults(func=ldap_action_ls(ldap_session, args.basedn))
        elif args.action == "modify":
            ldap_session = start_ldap_session(args.SERVER, args.BINDDN)
            ldap_modify.set_defaults(func=ldap_action_modify(ldap_session, \
                args.modify_dn, args.target_attr, args.new_value))
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


def ldap_action_modify(ldap_session, dn, attr, new_value):
    """ Modify LDAP attributes """
    logging.info("\nModifying LDAP attribute %s in %s!\n", attr, dn)
    attrs = retrieve_attrs_from_dn(ldap_session, dn)
    if attrs[0].get(attr):
        # Encode attribute to byte strings 
        new_value = [new_value.encode('utf-8')]
        # Do the actual operation!
        current_attr = attrs[0][attr]# [0].decode()
        old = {attr:current_attr}
        new = {attr:new_value}
        ldif = modlist.modifyModlist(old,new)
        ldap_session.modify_s(dn, ldif)
        logging.info("Previous %s attribute value: %s\nNew value: %s\n \
            ", attr, current_attr[0].decode(), new_value[0].decode())
    else:
        logging.critical("ERROR: No attribute %s was found!", attr)
        exit(0)
    ldap_session.unbind()


def ldap_action_delete(ldap_session, delete_dn):
    """ Delete an LDAP entry based on DN """
    logging.info("\nWARNING: you are about to delete the " \
    "following LDAP entry:\n\n %s\n", delete_dn)
    logging.info("\n##### This operation IS NOT REVERSIBLE!!!. " \
    "ALWAYS have a working backup first! #####\n")

    user_confirm = str(input("\nAre you sure you want to proceed? (YES/n)"))
    while user_confirm != "YES" and user_confirm != "n":
        user_confirm = str(input("Not a valid answer!. Proceed? (YES/n)"))
    if user_confirm == 'n':
        logging.info("\nOperation has been canceled!!\n")
        ldap_session.unbind()
        exit(0)
    else:
        ldap_session.delete_s(delete_dn)
        logging.info("\nLDAP entry %s has been removed!!\n", delete_dn)
        ldap_session.unbind()

if __name__ == "__main__":
    main()
