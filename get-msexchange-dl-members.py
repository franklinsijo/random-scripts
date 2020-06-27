#!/usr/bin/python3

from exchangelib import Credentials, Account, Folder, Configuration, DELEGATE

credentials = Credentials(username='username@organization.com', password='password')
config = Configuration(server='mail.organization.com', credentials=credentials)
account = Account(primary_smtp_address='username@organization.com', config=config, autodiscover=False, access_type=DELEGATE)

dl_address="dlname@organization.com"
for mailbox in account.protocol.expand_dl(dl_address):
    print(mailbox.email_address)
