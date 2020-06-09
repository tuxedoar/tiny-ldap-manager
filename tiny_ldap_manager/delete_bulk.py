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

""" LDAP delete in bulk functions for tiny-ldap-manager """
import logging
import ldap
from tiny_ldap_manager.tlmgr_core import ask_user_confirmation

def delete_entries_from_file(ldap_session, txtfile):
    """ Delete LDAP DNs retrieved from a text file """
    with open(txtfile, 'r') as f:
        target_entries = f.readlines()
        for each_entry in target_entries:
            each_entry = each_entry.strip('\n')
            # Check that DN is both valid and exists
            if ldap.dn.is_dn(each_entry):
                try:
                    ldap_session.delete_s(each_entry)
                    logging.info("Successfully removed LDAP entry: %s", each_entry)
                except ldap.NO_SUCH_OBJECT:
                    logging.warning("ERROR: %s does not exist!", \
                    each_entry)
            else:
                logging.warning("ERROR: %s is not a valid DN !.", \
                each_entry)


def ldap_delete_bulk(ldap_session, txtfile):
    """ Ask user confirmation and invoke function to delete entries in bulk """
    logging.info("WARNING: You are about to delete LDAP entries specified in " \
    "the following file:\n\n %s\n", txtfile)
    if ask_user_confirmation():
        try:
            delete_entries_from_file(ldap_session, txtfile)
        except IOError:
            logging.critical("\nERROR: file %s not found!", textfile)
