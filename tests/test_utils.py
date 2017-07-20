import os
import unittest

from odkim_rotate.utils import *

class ScrubTxtRecordTests(unittest.TestCase):
    def test_multiline_record(self):
        record = """20170409340._domainkey	IN	TXT	( "v=DKIM1; k=rsa; s=email; "
	  "p=MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAxA92JuwrAcRPmHgfr41ARdeh9quwG2r2IvuK5kPF5I4oEujDhcEexuUaDclJi4ztkioWCDDM1E2rNDFelcsvp7GgiP3mroiyeLKTh2zHXwfFNmDJrsfkGJcdGhcCN39/lXlmWx4NdJ1gFl2jiBxMXBhpbL1sm1pbC7kDfKEUc9HjgwLq+dNZTyd0+OOqtV4EZfxToA+RuvMnF2"
	  "u4PNYMqPJLghJv3T0o7LKSiRn/JJ8P7YuglI4IAB0pyUYvcWJhaNMYwCzevYgGBRj+TS+G2zT5UuirZ3VJ2yVlEjKrEBLMghlWocgzpwv23bP+lKRnLVsVEYKrO9cRCy8qbkXLGwIDAQAB" )  ; ----- DKIM key 20170409340 for example.com"""

        expected = "v=DKIM1; k=rsa; s=email; p=MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAxA92JuwrAcRPmHgfr41ARdeh9quwG2r2IvuK5kPF5I4oEujDhcEexuUaDclJi4ztkioWCDDM1E2rNDFelcsvp7GgiP3mroiyeLKTh2zHXwfFNmDJrsfkGJcdGhcCN39/lXlmWx4NdJ1gFl2jiBxMXBhpbL1sm1pbC7kDfKEUc9HjgwLq+dNZTyd0+OOqtV4EZfxToA+RuvMnF2u4PNYMqPJLghJv3T0o7LKSiRn/JJ8P7YuglI4IAB0pyUYvcWJhaNMYwCzevYgGBRj+TS+G2zT5UuirZ3VJ2yVlEjKrEBLMghlWocgzpwv23bP+lKRnLVsVEYKrO9cRCy8qbkXLGwIDAQAB"

        actual = scrub_txt_record(record)

        self.assertEqual(expected, actual)

    def test_singleline_record(self):
        record = """20170409340._domainkey	IN	TXT	( "v=DKIM1; k=rsa; s=email; p=MIIBIrO9cRCy8qbkXLGwIDAQAB" )  ; ----- DKIM key 20170409340 for example.com"""

        expected = "v=DKIM1; k=rsa; s=email; p=MIIBIrO9cRCy8qbkXLGwIDAQAB"

        actual = scrub_txt_record(record)

        self.assertEqual(expected, actual)

class CreateDnsProviderTests(unittest.TestCase):
    def test_linode(self):
        from odkim_rotate.dns.linode_provider import *

        os.environ['LINODE_API_KEY'] = ''
        provider = create_dns_provider('linode')
        self.assertIsInstance(provider, LinodeDnsProvider)

    def test_unknown(self):
        with self.assertRaises(NameError):
            provider = create_dns_provider('42')

