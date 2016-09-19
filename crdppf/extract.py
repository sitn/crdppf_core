# -*- coding: utf-8 -*-

import ast
from datetime import datetime

# MAIN DOCUMENT
class Extract(object):
    """The main class for the ectract object which collects all the data to write the report."""
    
    def __init__(self, request):
        # document id
        self.id = ''
        # sets the creation date of the PDF instance
        self.creationdate = datetime.now().strftime("%d.%m.%Y-%H:%M:%S")
        # same same but different use
        self.timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        # setting the default  root filename of the PDF and temporary files
        self.filename = 'thefilename'
        # report type: [reduced, reduced certified, complete, complete certified]
        self.reporttype = ''
        # output format of the report
        self.format = ''
        # basic configuration of the extract, like the language, translations and so on
        self.baseconfig = {}
        # empty dict for a list of  the topics and it's depending values
        self.topiclist = {}
        # dict holding the feature information
        self.feature = {}
        # parameters for the header
        self.header = {}
        # parameters for the footer
        self.footer = {}
        # array with specific data for the titlepage
        self.titlepage = {}
        # array holding the values for the table of content (toc)
        self.tocpage = {}
        # array containing the content of the topicpages
        self.topicpages = {}
        # array with the data of all appendices
        self.appendices = {}
        # array with list of the concerned documents
        self.doclist = []
        # dict used to store the entries of the table of content
        self.toc_entries = {}
        # dict to store the values of the appendix list
        self.appendix_entries = []
        # dict to store the refernces data
        self.reference_entries = []
        self.appendix_links = []
        self.basemap = {}
