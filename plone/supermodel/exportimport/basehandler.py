# -*- coding: utf-8 -*-
from lxml import etree
from plone.supermodel.debug import parseinfo
from plone.supermodel.interfaces import IDefaultFactory
from plone.supermodel.interfaces import IFieldExportImportHandler
from plone.supermodel.interfaces import IJSONFieldExportImportHandler
from plone.supermodel.interfaces import IXMLFieldExportImportHandler
from plone.supermodel.interfaces import IFieldNameExtractor
from plone.supermodel.utils import noNS
from plone.supermodel.utils import valueToElement
from plone.supermodel.utils import elementToValue
from zope.component import queryUtility
from zope.interface import Interface
from zope.interface import implementedBy
from zope.interface import implementer
from zope.schema.interfaces import IContextAwareDefaultFactory
from zope.schema.interfaces import IField
from zope.schema.interfaces import IVocabularyTokenized
from zope.schema.vocabulary import SimpleTerm
from zope.schema.vocabulary import SimpleVocabulary
import zope.schema

try:
    from collections import OrderedDict
except:
    from zope.schema.vocabulary import OrderedDict  # <py27


class OrderedDictField(zope.schema.Dict):
    _type = OrderedDict


class BaseHandler(object):
    """Base class for import/export handlers.

    The read_field method is called to read one field of the known subtype
    from an XML element.

    The write_field method is called to write one field to a particular element.
    """

    # Elements that we will not read/write. 'r' means skip when reading;
    # 'w' means skip when writing; 'rw' means skip always.

    filteredAttributes = {'order': 'rw', 'unique': 'rw', 'defaultFactory': 'w'}

    # Elements that are of the same type as the field itself
    fieldTypeAttributes = ('min', 'max', 'default', )

    # Elements that are of the same type as the field itself, but are
    # otherwise not validated
    nonValidatedfieldTypeAttributes = ('missing_value', )

    # Attributes that contain another field. Unfortunately,
    fieldInstanceAttributes = ('key_type', 'value_type', )

    # Fields that are always written

    forcedFields = frozenset(['default', 'missing_value'])

    def __init__(self, klass):
        self.klass = klass
        self.fieldAttributes = {}

        # Build a dict of the parameters supported by this field type.
        # Each parameter is itself a field, which can be used to convert
        # text input to an appropriate object.
        for schema in implementedBy(self.klass).flattened():
            self.fieldAttributes.update(zope.schema.getFields(schema))

        self.fieldAttributes['defaultFactory'] = zope.schema.Object(
            __name__='defaultFactory',
            title=u"defaultFactory",
            schema=Interface
        )

    def _constructField(self, attributes):
        return self.klass(**attributes)

