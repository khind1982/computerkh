# -*- mode: python -*-

import os

class Threading(object):
    # pylint: disable = E0203, W0621
    # We need to keep track of the current issue across
    # multiple invocations so we know when to start a new
    # collection of data.
    __shared_state = {
        'issue_data': [],
        'handled_docs': 0,
    }

    def __init__(self, dest_root, nsmap, messagequeue):
        self.__dict__ = self.__shared_state
        self.dest_root = dest_root
        self.nsmap = nsmap
        self.msq = messagequeue

    def handle_document(self, document, issueid, articles_in_issue):
        # pylint: disable = W0201
        self.document = document
        docid = document.xpath('//dc:identifier', namespaces=self.nsmap)[0].text
        pages = [img for img in document.xpath('//x:pagemap/x:page/@image',
                                               namespaces=self.nsmap)]
        for page in pages:
            self.issue_data.append('%(docid)s\t%(pgimg)s\n' % {
                'docid': docid, 'pgimg': page
            })
        self.handled_docs += 1

        if self.handled_docs == articles_in_issue:
            self.flush_to_disk(issueid)
            self.handled_docs = 0
            self.issue_data = []

    def flush_to_disk(self, issueid):
        ''' When we have handled all pages in the issue, we call this
        method which writes the collected data into the appropriate
        threading file.'''
        year, month = issueid[0:4], issueid[4:6]
        issue_path = os.path.join(self.dest_root, year, month)
        thr_file = os.path.join(issue_path, "%s.txt" % issueid)
        os.makedirsp(issue_path) # pylint: disable = E1101
        with open(thr_file, 'w') as outf:
            for image in self.issue_data:
                outf.write(image)
