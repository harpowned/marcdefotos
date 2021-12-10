#!/usr/bin/python
import imaplib
import time
import email
import os

imap_user = "marcdefotos@exampleserver.com"
imap_pass = "some_imap_password"
imap_server = "exampleserver.com"
imap_port = 993
imap_folder_name = "INBOX"


dst_folder="/home/harpo/marc_de_fotos"

print "Connecting to source %s:%s" % (imap_server,imap_port)
#src_conn = imaplib.IMAP4(imap_server,imap_port)
src_conn = imaplib.IMAP4_SSL(imap_server,imap_port)
src_conn.login(imap_user,imap_pass)

while True:
	src_select = src_conn.select(imap_folder_name, readonly = False)
	resp, items = src_conn.search(None, 'ALL')
	print items
	msg_nums = items[0].split()
	print '%s messages to archive' % len(msg_nums)
	for msg_num in msg_nums:
		print "Archiving message %s" % msg_num
		resp, data = src_conn.fetch(msg_num, "(FLAGS INTERNALDATE BODY.PEEK[])") # get email
		if resp != "NO":
			message = data[0][1]

			msg = email.message_from_string(message)
			for part in msg.walk():
				print "Processing message part"
				if part.get_content_maintype() == 'multipart':
					print "Message is multipart"
					continue
				if part.get('Content-Disposition') is None:
					print "Content-disposition is none"
					continue
				filename = part.get_filename()
				att_path = os.path.join(dst_folder, filename)
				if not os.path.isfile(att_path):
					print "Writing file"
					fp = open(att_path, 'wb')
					fp.write(part.get_payload(decode=True))
					fp.close()
				else:
					print "File already exists"

			src_conn.copy(msg_num,'Trash')
			del_msg = src_conn.store(msg_num, '+FLAGS', '\\Deleted') # mark for deletion
	ex = src_conn.expunge() # delete marked
	print 'expunge status: %s' % ex[0]
	if not ex[1][0]: # result can be ['OK', [None]] if no messages need to be deleted
		print 'expunge count: 0'
	else:
		print 'expunge count: %s' % len(ex[1])

	time.sleep(34)
