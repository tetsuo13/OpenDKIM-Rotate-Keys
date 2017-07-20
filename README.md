# OpenDKIM Key Rotate

[![Travis](https://img.shields.io/travis/rust-lang/rust.svg)](https://travis-ci.org/tetsuo13/OpenDKIM-Rotate-Keys)

Automates the task of rotating OpenDKIM keys by generating new keys for the
existing domains in a temporary location, creating new DNS entries in Linode,
and installing the keys to production.

It will perform the following tasks:

1. Generate a new key for each domain configured to use OpenDKIM to a
   temporary directory.
  * The selector will be today's date in *YYYYMMDD* format with
    microseconds. This allows you to generate keys multiple times in a single
    day while still providing some level of anonymity to cloak when it was
    created.
  * Temporary directory which contains the public and private keys will be
    readable only by root.
2. Create new TXT DNS records using the new selector. Currently only supports
   the Linode API but other DNS providers can be added.
3. Script will pause and wait for user input before installing the keys. This
   allows DNS changes to take effect.
4. Verifies the setup of signing and verifying (private and public) keys; and,
   if successful:
5. Installs private keys
6. Update KeyTable with new selector for domains.
6. Restarts Postfix and OpenDKIM daemons.

Note that this script was initially created to automate this rather simple but
error prone set of tasks that make up the OpenDKIM key rotation
responsibility that needs to occur at most every few months. It was created
specifically for a certain mail system that runs Ubuntu, Postfix, and OpenDKIM
from Apt sources although modifications to handle other configurations are
certainly welcome.

# System Configuration

Script makes several assumptions about the system it's being run on.
Specifically:

- Python 2.7 or greater. Untested with Python 3 but may work.
- [OpenDKIM](http://opendkim.org/) is installed using Apt.
- OpenDKIM is configured to use the "KeyTable" data set. Example settings
  relevant to this script:```
KeyTable            /etc/dkimkeys/key.table
SigningTable        refile:/etc/dkimkeys/signing.table
```
- Path to OpenDKIM configuration `/etc/opendkim.conf`

# Usage

Script must be run as root.

Add the Linode API key as an environment variable `LINODE_API_KEY` prior to
running.

```shell
$ sudo rotate_opendkim_keys.py
```

It will generate private and public keys for each domain listed in OpenDKIM's
config, displaying the domain and steps taken along the way.

At this point the script will pause before continuing. This is intended as a
way to let DNS propegate as the OpenDKIM testing process will use DNS to
verify the keys.

After some amount of time press any key to continue. For reference, Linode
typically takes at least 15 minutes.

The
(http://www.opendkim.org/opendkim-testkey.8.html)[OpenDKIM filter installation test]
will then test each of the new keys. If they all succeed then the new keys
will be installed and the Postfix and OpenDKIM daemons are restarted.

