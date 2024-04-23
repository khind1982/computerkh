#!/usr/local/bin/python2.6
# -*- mode: python -*-

import sys, os, site
sys.path.append(os.path.join(os.path.dirname(__file__) + '/../lib/python'))
sys.path.append('../lib')
site.addsitedir('/packages/dsol/lib/python2.6/site-packages') #pylint:disable=E1101

import socket

from monkeypatches.elixirpatches import * #pylint:disable=W0622,W0401,W0614 

options_defaults['table_options'] = dict(mysql_engine="InnoDB")

if socket.gethostname() == 'dsol.private.chadwyck.co.uk':
    metadata.bind = "mysql://mstarss:mstarss@localhost/mshh2?unix_socket=/tmp/mysql.sock"
else:
    metadata.bind = "mysql://mstarss:mstarss@dsol.private.chadwyck.co.uk/mshh2"

# This model just defines the bare minimum schema to produce the output
# files for hit highlighting. It is up to the per-product module to 
# extract the relevant bits and pieces to populate the database
# according to this schema.

class Product(Entity):
    using_options(tablename='products')
    name = Field(String(24), unique=True, index=True)

    has_many('articles', of_kind='Article')

# This class is deliberately denormalised. Since this schema describes
# a database used for temperary storage of specific values, which are deleted
# often, it doesn't hurt to carry a bit of repeated information on each article
# row. This should also be a little faster than having additional tables to 
# carry the associated values.
class Article(Entity):
    using_options(tablename='articles')
    uid = Field(String(34), index=True, unique=True)
    journalid = Field(String(56), index=True)
    outputdir = Field(String(128))
    currentsession = Field(String(128), index=True)  # The PID of the current process

    has_many('pages', of_kind='Page', lazy=True)
    belongs_to('product', of_kind='Product', lazy=True)

class Page(Entity):
    using_options(tablename='pages')
    uid = Field(String(72), index=True, unique=True)

    belongs_to('article', of_kind='Article', onupdate='cascade', ondelete='cascade', lazy=True)
    has_many('words', of_kind='Word', lazy=True)

    def __init__(self, uid=None): #pylint:disable=W0231
        if uid is not None:
            self.uid = uid

class Word(Entity):
    using_options(tablename='words')
    value = Field(String(156))
    coords = Field(String(32))
#    ulx = Field(Integer())
#    uly = Field(Integer())
#    lrx = Field(Integer())
#    lry = Field(Integer())

    belongs_to('page', of_kind='Page', onupdate='cascade', ondelete='cascade', lazy=True)

    def __init__(self, value=None, coords=None): #pylint:disable=W0231
        if value is not None:
            self.value = value
        if coords is not None:
            self.coords = coords
#        if coords is not None:
#            for k in coords.keys():
#                setattr(self, k, coords[k])

#    def __str__(self):
#        return self.formatted_for_output

    @property
    def formatted_for_output(self):
#        points = ':'.join([str(getattr(self, point)) for point in ['ulx', 'uly', 'lrx', 'lry']])
        return ':'.join([self.value, self.coords])

setup_all(True)
