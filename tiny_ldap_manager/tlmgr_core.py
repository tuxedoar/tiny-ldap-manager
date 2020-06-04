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

""" Core helper functions for tiny-ldap-manager """

import logging
import ldap
import getpass

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

def ask_user_confirmation():
    """ Ask for user confirmation """
    user_confirm = str(input("Are you sure you wanna proceed? (YES/n)"))
    while user_confirm not in("YES", "n"):
        user_confirm = str(input("Not a valid answer!. Proceed? (YES/n)"))
    if user_confirm == 'n':
        logging.info("\nOperation has been canceled!!\n")
        user_confirm = False
    else:
        user_confirm = True
    return user_confirm


def retrieve_attrs_from_dn(ldap_session, basedn):
    """ Retrieve attributes from a given DN """
    ldap_data = ldap_session.search_s(basedn, ldap.SCOPE_BASE, 'objectClass=*')
    attrs = [i[1] for i in ldap_data]
    return attrs
