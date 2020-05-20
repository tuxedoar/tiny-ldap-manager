#!/home/fulano/python-ldap/env/bin/python3

# Usage should look like this:
#   tiny-ldap-manager [SERVER] [BIND_DN] [ACTION] [SUB-ACTION]
#

# https://rosettacode.org/wiki/Active_Directory/Search_for_a_user#Python
# http://www.grotan.com/ldap/python-ldap-samples.html
# https://gist.github.com/amarao/36327a6f77b86b90c2bca72ba03c9d3a (example ofargparse)
# 

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
    # LDAP available operations to perform!!:
    subparser = parser.add_subparsers(dest='action')
    # List LDAP attributes from DN!
    ldap_ls = subparser.add_parser('ls', \
            help='List LDAP attributes for specified DN')
    ldap_ls.add_argument('basedn')
    # Modify existing LDAP attributes
    ldap_modify = subparser.add_parser('modify', \
            help="Modify an LDAP attribute")
    ldap_modify.add_argument('target_dn')
    ldap_modify.add_argument('target_attr')
    ldap_modify.add_argument('new_value')
    args = parser.parse_args()

    try:
        #if args.action != None:
        if args.action == "ls":
            ldap_session = start_ldap_session(args.SERVER, args.BINDDN)
            ldap_ls.set_defaults(func=ldap_action_ls(ldap_session, args.basedn))
        elif args.action == "modify":
            ldap_session = start_ldap_session(args.SERVER, args.BINDDN)
            ldap_modify.set_defaults(func=ldap_action_modify(ldap_session, \
                args.target_dn, args.target_attr, args.new_value))
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
    attrs = retrieve_attrs_from_dn(ldap_session, basedn)
    for key, value in attrs[0].items():
        print("{}:\t{}".format(key, value[0].decode()))


def retrieve_attrs_from_dn(ldap_session, basedn):
    """ Retrieve attributes from given DN """
    logging.info("\nShowing  attributes for: {}:\n\n".format(basedn))
    ldap_data = ldap_session.search_s(basedn, ldap.SCOPE_BASE, 'objectClass=*')
    attrs = [i[1] for i in ldap_data]
    ldap_session.unbind()
    return attrs

def ldap_action_modify(ldap_session, dn, attr, new_value):
    """ Modify LDAP attributes """
    logging.info("\nLet's modify an LDAP attribute!\n")
    ldap_data = ldap_session.search_s(dn, ldap.SCOPE_BASE, 'objectClass=*')
    attrs = [i[1] for i in ldap_data]
    if attrs[0].get(attr):
        # Encode attribute to byte strings 
        new_value = [new_value.encode('utf-8')]
        # Do the actual operation!
        current_attr = attrs[0][attr]# [0].decode()
        old = {attr:current_attr}
        new = {attr:new_value}
        ldif = modlist.modifyModlist(old,new)
        ldap_session.modify_s(dn, ldif)
        logging.info("Current attribute %s value: %s\nNew value: %s\n \
            ".format(attr, current_attr, new_value))
    else:
        logging.critical("ERROR: No attribute %s was found!", attr)
        exit(0)

if __name__ == "__main__":
    main()
