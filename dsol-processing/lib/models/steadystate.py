# -*- mode: python -*-

from datetime import datetime

# The monkeypatches.elixirpatches module defines the method get_by_or_create.
# It also imports all of elixir's contents, so just importing it here works
# as expected. This is probably a cardinal sin among those who care...
from monkeypatches.elixirpatches import *  #pylint:disable=W0622,W0401,W0614

# Set the default table type to InnoDB
options_defaults['table_options'] = dict(mysql_engine="InnoDB")

metadata.bind = "mysql://mstarss:mstarss@dsol.private.chadwyck.co.uk/steadystate"
#metadata.bind.echo = True
#metadata.bind = "sqlite:////tmp/steadystate.sqlite"

class Article(Entity):
    using_options(tablename='articles')
    uid = Field(String(34), index=True)

    belongs_to('publication', of_kind='Publication')
    belongs_to('product', of_kind='Product')

    has_many('checksums', of_kind='Checksum')

    def __init__(self, uid=None):
        super(self.__class__, self).__init__()
        self.uid = uid

    @property
    def transformations(self):
        return session.query(Transformation).join('checksums').filter(Article.uid == self.uid).all() #pylint:disable=E1101

    # Compare the passed-in checksum with the most recently registered one
    # in the database. Return values:
    #  0 - checksums match - no steady state update needed
    #  1 - checksums differ - trigger steady state update
    # -1 - no previous checksum in database - trigger creation and registration of new record.

    def compare_checksums(self, checksum):
        try:
            if checksum == self.checksums[-1].token:  #pylint:disable=E1101
                return 0
            else:
                return 1
        except IndexError:
            return -1    

    def update_checksums(self, sstoken, transformation):
        checksum = Checksum.get_by_or_create(token=sstoken)
        checksum.transformations.append(transformation)
        if checksum not in self.checksums:   #pylint:disable=E1101
            self.checksums.append(checksum)  #pylint:disable=E1101
        elixir.session.commit()              #pylint:disable=E1101

class Product(Entity):
    using_options(tablename='products')
    title = Field(String(12), unique=True)

    has_many('articles', of_kind='Article')
    has_many('publications', through='articles', via='publication')
    has_many('transformations', of_kind='Transformation')

    def __init__(self, title=None):
        super(self.__class__, self).__init__()
        self.title = title

    @property
    def most_recent_transformation(self):
        return self.transformations[-1]  #pylint:disable=E1101

class Publication(Entity):
    using_options(tablename='publications')
    jid = Field(String(30))

    has_many('articles', of_kind='Article')
    has_many('products', through='articles', via='product')

    def __init__(self, jid=None):
        super(self.__class__, self).__init__()
        self.jid = jid

class Checksum(Entity):
    using_options(tablename='checksums')
    token = Field(String(128), unique=True, index=True)

    belongs_to('article', of_kind='Article')
    has_and_belongs_to_many('transformations', of_kind='Transformation')

    def __init__(self, token=None):
        super(self.__class__, self).__init__()
        self.token = token

class Transformation(Entity):
    using_options(tablename='transformations')
    token = Field(String(64), unique=True, index=True)
    created_at = Field(DateTime)

    checksums = elixir.ManyToMany('Checksum', ondelete='cascade', onupdate='cascade')
    has_many('articles', through='checksums', via='article')

    belongs_to('product', of_kind='Product')

    def __init__(self, token=None):
        super(self.__class__, self).__init__()
        self.token = token
        self.created_at = datetime.now()

    def find_previously_seen_article(self, article):
        return session.query(Article).join('checksums').filter(Article.uid == article.uid).first() #pylint:disable=E1101

setup_all(True)
