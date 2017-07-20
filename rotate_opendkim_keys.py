#!/usr/bin/env python

import grp
import os
import pwd
import sys

from odkim_rotate.key_table import *
from odkim_rotate.manager import *
from odkim_rotate.utils import *

def main(verbose):
    manager = Manager(verbose)
    manager.opendkim_conf = '/etc/opendkim.conf'
    manager.opendkim_keys_basedir = '/etc/dkimkeys'
    manager.opendkim_genkey = '/usr/bin/opendkim-genkey'
    manager.opendkim_testkey = '/usr/bin/opendkim-testkey'
    manager.key_owner = 'opendkim'
    manager.key_owner_uid = pwd.getpwnam(manager.key_owner).pw_uid
    manager.key_group = 'opendkim'
    manager.key_group_gid = grp.getgrnam(manager.key_group).gr_gid

    manager.dns_provider = create_dns_provider('linode')
    manager.keytable_path = get_keytable_path(manager.opendkim_conf)

    manager.keytable = KeyTable(manager.keytable_path)

    manager.rotate_keys()

if __name__ == '__main__':
    if os.getenv('USER') != 'root':
        sys.exit('Error: script must be run as root')

    main(len(sys.argv) == 2 and sys.argv[1] == '-v')

