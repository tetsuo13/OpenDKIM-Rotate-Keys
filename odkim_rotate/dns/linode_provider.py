import os
import requests

from odkim_rotate.dns.provider import *

class LinodeDnsProvider(DnsProvider):
    """DNS provider for Linode.

    Linode requires a domain ID when adding any DNS records. Rather than
    enumerating all domains on every request to create a TXT record in order
    to find the ID of the domain in use, all domains for the Linode account
    are cached in memory so that subsequent requests are faster. This opens
    the possibility of errors if the domain on Linode is deleted after its
    information has been cached.

    Full documentation on Linode API:
    https://www.linode.com/api/
    """

    api_key = ''
    api_url = 'https://api.linode.com/'
    domains = {}

    def __init__(self):
        if 'LINODE_API_KEY' not in os.environ:
            raise KeyError('LINODE_API_KEY environment variable not set')

        self.api_key = os.environ.get('LINODE_API_KEY')
        self.domains = {}

    def create_txt_record(self, domain, selector, value):
        if not self.domains:
            self.enumerate_domains()

        if domain not in self.domains:
            raise KeyError('Domain {} not found in Linode'.format(domain))

        data = {
            'api_action': 'domain.resource.create',
            'DomainID': self.domains[domain],
            'Type': 'TXT',
            'Name': selector + '._domainkey',
            'Target': value
        }

        r = self.send_request(data)

    def enumerate_domains(self):
        """Cache all domains available along with their domain ID.
        """

        data = {
            'api_action': 'domain.list'
        }

        r = self.send_request({'api_action': 'domain.list'})

        for domain in r['DATA']:
            self.domains[domain['DOMAIN']] = domain['DOMAINID']

        if len(self.domains) == 0:
            raise RuntimeError('No domains found on Linode')

    def send_request(self, data):
        headers = {
            'User-Agent': 'OpenDKIMRotateKeys/1.0.0'
        }

        data['api_key'] = self.api_key

        r = requests.post(self.api_url, data=data, headers=headers).json()

        if len(r['ERRORARRAY']) > 0:
            messages = []

            for error in r['ERRORARRAY']:
                msg = '{} (code {})'.format(error['ERRORMESSAGE'],
                                            error['ERRORCODE'])
                messages.append(msg)

            raise RuntimeError('Errors from Linode: {}'.format(', '.join(messages)))

        return r

