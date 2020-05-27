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

""" Helper functions for the 'modify' LDAP related operations """

import logging
import ldap
import ldap.modlist as modlist
from tiny_ldap_manager.tlmgr_core import ask_user_confirmation


def ldap_replace_attr(ldap_session, attrs, attr, dn, new_value):
    """ Replace an existing LDAP attribute's value """
    # Do the actual operation!
    current_attr = attrs[0][attr]
    old = {attr:current_attr}
    new = {attr:new_value}
    ldif = modlist.modifyModlist(old, new)
    ldap_session.modify_s(dn, ldif)
    logging.info("\nAttribute %s value has been changed:\n\n" \
    " Previous value: %s\n New value: %s\n" \
    , attr, current_attr[0].decode(), new_value[0].decode())


def ldap_add_attr(ldap_session, dn, attr, value):
    """ Add attribute in LDAP entry if NOT exists  """
    new_attr = [(ldap.MOD_ADD, attr, value)]
    ldap_session.modify_s(dn, new_attr)
    logging.info("A new attribute has been added:\n\n %s: %s\n", \
                attr, value[0].decode())


def ldap_delete_attr(ldap_session, dn, attr):
    """ Delete an attribute from LDAP entry """
    logging.info("The following attribute from %s will be removed:\n\n%s\n", dn, attr)
    if ask_user_confirmation():
        ldap_session.modify_s(dn, [(ldap.MOD_DELETE, attr, None)])
        logging.info("\nLDAP attribute %s has been removed!!\n", attr)
