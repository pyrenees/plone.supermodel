# -*- coding: utf-8 -*-
from plone.supermodel.utils import valueToElement
from plone.supermodel.utils import elementToValue
from zope.interface import Interface
from zope.interface import implementedBy
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


class DictHandler(BaseHandler):
    """Special handling for the Dict field, which uses Attribute instead of
    Field to describe its key_type and value_type.
    """

    def __init__(self, klass):
        super(DictHandler, self).__init__(klass)
        self.fieldAttributes['key_type'] = zope.schema.Field(
            __name__='key_type',
            title=u"Key type"
        )
        self.fieldAttributes['value_type'] = zope.schema.Field(
            __name__='value_type',
            title=u"Value type"
        )


class ObjectHandler(BaseHandler):
    """Special handling for the Object field, which uses Attribute instead of
    Field to describe its schema
    """

    # We can't serialise the value or missing_value of an object field.

    filteredAttributes = BaseHandler.filteredAttributes.copy()
    filteredAttributes.update({'default': 'w', 'missing_value': 'w'})

    def __init__(self, klass):
        super(ObjectHandler, self).__init__(klass)

        # This is not correctly set in the interface
        self.fieldAttributes['schema'] = zope.schema.InterfaceField(
            __name__='schema'
        )


class ChoiceHandler(BaseHandler):
    """Special handling for the Choice field
    """

    filteredAttributes = BaseHandler.filteredAttributes.copy()
    filteredAttributes.update(
        {'vocabulary': 'w',
         'values': 'w',
         'source': 'w',
         'vocabularyName': 'rw'
         }
    )

    def __init__(self, klass):
        super(ChoiceHandler, self).__init__(klass)

        # Special options for the constructor. These are not automatically
        # written.

        self.fieldAttributes['vocabulary'] = zope.schema.TextLine(
            __name__='vocabulary',
            title=u"Named vocabulary"
        )

        self.fieldAttributes['values'] = zope.schema.List(
            __name__='values',
            title=u"Values",
            value_type=zope.schema.Text(title=u"Value")
        )

        # XXX: We can't be more specific about the schema, since the field
        # supports both ISource and IContextSourceBinder. However, the
        # initialiser will validate.
        self.fieldAttributes['source'] = zope.schema.Object(
            __name__='source',
            title=u"Source",
            schema=Interface
        )

    def readAttribute(self, element, attributeField):
        if (
            element.tag == 'values' and
            any([child.get('key') for child in element])
        ):
            attributeField = OrderedDictField(
                key_type=zope.schema.TextLine(),
                value_type=zope.schema.TextLine(),
            )
        return elementToValue(attributeField, element)

    def _constructField(self, attributes):
        if 'values' in attributes:
            if isinstance(attributes['values'], OrderedDict):
                attributes['values'] = attributes['values'].items()
            terms = []
            for value in attributes['values']:
                title = (value or u'')
                if isinstance(value, tuple):
                    value, title = value
                encoded = (value or '').encode('unicode_escape')
                if value != encoded:
                    value = value or u''
                    term = SimpleTerm(
                        token=encoded,
                        value=value,
                        title=title
                    )
                else:
                    term = SimpleTerm(value=value, title=title)
                terms.append(term)
            attributes['vocabulary'] = SimpleVocabulary(terms)
            del attributes['values']
        return super(ChoiceHandler, self)._constructField(attributes)

    def write(self, field, name, type, elementName='field'):

        element = super(ChoiceHandler, self).write(
            field,
            name,
            type,
            elementName
        )

        # write vocabulary or values list

        # Named vocabulary
        if field.vocabularyName is not None and field.vocabulary is None:
            attributeField = self.fieldAttributes['vocabulary']
            child = valueToElement(
                attributeField,
                field.vocabularyName,
                name='vocabulary',
                force=True
            )
            element.append(child)

        # Listed vocabulary - attempt to convert to a simple list of values
        elif (
            field.vocabularyName is None and
            IVocabularyTokenized.providedBy(field.vocabulary)
        ):
            value = []
            for term in field.vocabulary:
                if (
                    not isinstance(term.value, (str, unicode), ) or
                    term.token != term.value.encode('unicode_escape')
                ):
                    raise NotImplementedError(
                        u"Cannot export a vocabulary that is not "
                        u"based on a simple list of values"
                    )
                if term.title and term.title != term.value:
                    value.append((term.value, term.title))
                else:
                    value.append(term.value)

            attributeField = self.fieldAttributes['values']
            if any(map(lambda v: isinstance(v, tuple), value)):
                def _pair(v):
                    return v if len(v) == 2 else (v[0],) * 2
                value = OrderedDict(map(_pair, value))
                attributeField = OrderedDictField(
                    key_type=zope.schema.TextLine(),
                    value_type=zope.schema.TextLine(),
                )
            child = valueToElement(
                attributeField,
                value,
                name='values',
                force=True
            )
            element.append(child)

        # Anything else is not allowed - we can't export ISource/IVocabulary or
        #  IContextSourceBinder objects.
        else:
            raise NotImplementedError(
                u"Choice fields with vocabularies not based on "
                u"a simple list of values or a named vocabulary "
                u"cannot be exported"
            )

        return element
