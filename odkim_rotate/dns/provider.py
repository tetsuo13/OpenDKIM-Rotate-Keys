import os

class DnsProvider:
    """DNS provider.
    """

    def create_txt_record(self, domain, selector, value):
        raise NotImplementedError()

