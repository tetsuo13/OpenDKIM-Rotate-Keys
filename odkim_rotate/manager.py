import datetime
import os
import shutil
import subprocess
import tempfile

from odkim_rotate.key_table import *
from odkim_rotate import utils

class Manager:
    def __init__(self, verbose):
        self.verbose = verbose
        self.scratch_dir = tempfile.mkdtemp()
        self.starting_dir = os.getcwd()

        # Today's date with microseconds for "randomization."
        self.selector = datetime.datetime.now().strftime('%Y%m%d%f')

    def print_config(self):
        utils.print_verbose('OpenDKIM config: ' + self.opendkim_conf)
        utils.print_verbose('OpenDKIM KeyTable directory: ' + self.opendkim_keys_basedir)
        utils.print_verbose('OpenDKIM generate key: ' + self.opendkim_genkey)
        utils.print_verbose('OpenDKIM test key: ' + self.opendkim_genkey)
        utils.print_verbose('Private keys ownership: {}:{} ({}:{})'.format(self.key_owner, \
                                                                           self.key_group, \
                                                                           self.key_owner_uid, \
                                                                           self.key_group_gid))
        utils.print_verbose('OpenDKIM KeyTable file: ' + self.keytable_path)
        utils.print_verbose('Using scratch directory ' + self.scratch_dir)

    def generate_keys(self):
        for short_name, values in self.keytable:
            utils.print_header('Processing ' + values[KeyTable.DOMAIN])

            print('Generating key...')

            options = [
                self.opendkim_genkey, \
                '--bits=2048', \
                #'--hash-algorithms=rsa-sha256', \
                '--restrict', \
                '--selector=' + self.selector, \
                '--domain=' + values[KeyTable.DOMAIN], \
            ]

            if self.verbose:
                options.append('--verbose')
                print('\x1b[1;30;40m')

            subprocess.check_call(options)

            if self.verbose:
                print('\x1b[0m')

            os.rename(self.selector + '.private', short_name + '.private')
            os.rename(self.selector + '.txt', short_name + '.txt')

            self.keytable.update_selector(short_name, self.selector)

            print('Adding DNS TXT record...')

            with open(short_name + '.txt', 'r') as f:
                txt_value = utils.scrub_txt_record(f.read())

            if self.verbose:
                utils.print_verbose(txt_value)

            self.dns_provider.create_txt_record(values[KeyTable.DOMAIN],
                                                self.selector, txt_value)

    def test_keys(self):
        utils.print_header('Testing keys...')
        print('')

        for short_name, values in self.keytable:
            utils.print_header('Testing {}...'.format(values[KeyTable.DOMAIN]))

            options = [
                self.opendkim_testkey, \
                '-d', values[KeyTable.DOMAIN], \
                '-s', values[KeyTable.SELECTOR], \
                '-k', short_name + '.private' \
            ]

            if self.verbose:
                options.append('-vvv')
                print('\x1b[1;30;40m')

            result = subprocess.check_call(options)

            if self.verbose:
                print('\x1b[0m')

            if result != 0:
                utils.print_error('FAILED!')
                # TODO: Show result from opendkim_testkey
                print('')
                utils.print_error('Rotating keys aborted.')
                return False

            print('')

        return True

    def install_keys(self):
        print('')
        utils.print_header('Installing keys...')
        print('')

        utils.toggle_services(True)
        print('')

        try:
            for short_name, values in self.keytable:
                utils.print_header('Installing {}...'.format(values[KeyTable.DOMAIN]))

                local_key = short_name + '.private'

                if self.verbose:
                    utils.print_verbose('Moving {} to {}'.format(local_key,
                                                                 values[KeyTable.PRIVATE_KEY]))

                os.rename(local_key, values[KeyTable.PRIVATE_KEY])
                os.chown(values[KeyTable.PRIVATE_KEY], self.key_owner_uid,
                         self.key_group_gid)

            try:
                utils.print_header('Saving new selector to KeyTable file...')
                self.keytable.save_changes()
            except Exception as e:
                utils.print_error('Error: Unable to save new selector to KeyTable file: ' + str(e))

                try:
                    self.keytable.revert_changes()
                except Exception as ex:
                    utils.print_error('Error: Unable to revert changes made to KeyTable file: ' + str(ex))
        except Exception as e:
            utils.print_error('Error: Unable to install key: ' + str(e))
        finally:
            print('')
            utils.toggle_services(False)

    def rotate_keys(self):
        if self.verbose:
            self.print_config()

        print('Processing {:,} domains...'.format(len(self.keytable)))
        print('Using selector ' + self.selector)
        print('')

        try:
            os.chdir(self.scratch_dir)
            self.generate_keys()

            try:
                input = raw_input
            except NameError:
                pass

            print('')
            print('')
            utils.print_header('Wait for DNS changes to propagate before continuing.')
            utils.print_header('The time is now {}'.format(datetime.datetime.now().strftime('%c')))
            input('Press any key to continue with checking DNS and installing keys...')
            print('')
            print('')

            test_results = self.test_keys()

            if test_results:
                self.install_keys()
        finally:
            os.chdir(self.starting_dir)
            shutil.rmtree(self.scratch_dir)

        print('')

