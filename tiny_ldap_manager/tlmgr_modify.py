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

from sys import exit
import logging
import ldap
import ldap.modlist as modlist
from tiny_ldap_manager.tlmgr_core import ask_user_confirmation
from tiny_ldap_manager.tlmgr_core import retrieve_attrs_from_dn
from tiny_ldap_manager.tlmgr_csv import read_csv
from tiny_ldap_manager.tlmgr_csv import sanitize_csv_entry
from tiny_ldap_manager.tlmgr_csv import csv_sanitizer

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


def process_each_bulk_entry(ldap_session, attr, each_entry):
    """ Auxiliary function to modify or add LDAP attributes in bulk  """
    try:
        for entry in each_entry:
            dn = each_entry.get('dn')
            attr_value = each_entry[attr]
        logging.info("\nProcessing DN in CSV: %s", dn)
        # Is DN valid?
        if dn != None and ldap.dn.is_dn(dn):
            # Check if given attribute already exists!
            existing_attrs = retrieve_attrs_from_dn(ldap_session, dn)
            does_attr_exist = existing_attrs[0].get(attr)
            # Add or modify attribute
            if does_attr_exist != None:
                # We modify existing attribute
                new_value = [attr_value.encode('utf-8')]
                ldap_replace_attr(ldap_session, existing_attrs, attr, dn, new_value)
            else:
                # We create the attribute
                value = [attr_value.encode('utf-8')]
                ldap_add_attr(ldap_session, dn, attr, value)
        else:
            logging.warning("ERROR - Invalid or inexisting LDAP key used for DN on CSV\n")
    except (ldap.NO_SUCH_OBJECT, ldap.INVALID_SYNTAX, ldap.UNDEFINED_TYPE) as err:
        logging.critical(err)


def ldap_modify_bulk(ldap_session, csv_file):
    """ Modify LDAP attributes in bulk based on a CSV file """
    logging.info("\nATTENTION: Several LDAP attributes will be changed given " \
    "the specified CSV file!\n")
    if ask_user_confirmation():
        # Perform a sanity check of the CSV file
        sanitized_csv = csv_sanitizer(csv_file)
        # Check CSV sanity results and act accordingly! 
        for csv_entry in sanitized_csv:
            # We only process those CSV entries where the overall result of
            # its sanity check was 'True'.
            if True in csv_entry:
                # Get CSV columns
                csv_cols = [i for i in csv_entry[0]]
                # We assume 2nd CSV col is attribute's name!
                attr = csv_cols[1]
                process_each_bulk_entry(ldap_session, attr, csv_entry[0])
            else:
                logging.warning("\nERROR: Wrong CSV formatted content found!")
