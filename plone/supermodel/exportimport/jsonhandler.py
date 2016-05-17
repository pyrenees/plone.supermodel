# -*- coding: utf-8 -*-
import json
from lxml import etree
from plone.supermodel.debug import parseinfo
from plone.supermodel.exportimport import BaseHandler
from plone.supermodel.interfaces import IDefaultFactory
from plone.supermodel.interfaces import IFieldExportImportHandler
from plone.supermodel.interfaces import IJSONFieldExportImportHandler
from plone.supermodel.interfaces import IFieldNameExtractor
from plone.supermodel.utils import noNS
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



from zope.schema.interfaces import ICollection
from zope.schema.interfaces import IDict
from zope.schema.interfaces import IField
from zope.schema.interfaces import IFromUnicode
from plone.supermodel.interfaces import IToUnicode


def valueToElement(field, value, name=None, force=False):
    """Create and return an element that describes the given value, which is
    assumed to be valid for the given field.

    If name is given, this will be used as the new element name. Otherwise,
    the field's __name__ attribute is consulted.

    If force is True, the value will always be written. Otherwise, it is only
    written if it is not equal to field.missing_value.
    """

    if name is None:
        name = field.__name__

    child = {'type': value.__class__.__name__}

    if value is not None and (force or value != field.missing_value):

        if IDict.providedBy(field):
            key_converter = IToUnicode(field.key_type)
            for k, v in value.items():
                name, list_element = valueToElement(field.value_type, v, 'element', force)
                list_element['key'] = key_converter.toUnicode(k)
                child['values'].append(list_element)

        elif ICollection.providedBy(field):
            for v in value:
                name, list_element = valueToElement(field.value_type, v, 'element', force)
                child['values'].append(list_element)

        else:
            converter = IToUnicode(field)
            child['value'] = converter.toUnicode(value)

            # handle i18n
            # if isinstance(value, Message):
            #     child.set(ns('domain', I18N_NAMESPACE), value.domain)
            #     if not value.default:
            #         child.set(ns('translate', I18N_NAMESPACE), '')
            #     else:
            #         child.set(ns('translate', I18N_NAMESPACE), child.text)
            #         child.text = converter.toUnicode(value.default)

    return name, child


@implementer(IJSONFieldExportImportHandler)
class JSONBaseHandler(BaseHandler):

    def read(self, element):
        """Read a field from the element and return a new instance
        """
        raise NotImplementedError("TODO: This.")

    def write(self, field, name, element_type, element_name='field'):
        """Create and return a new element representing the given field
        """

        element = {'type': element_type}

        for attribute_name in sorted(self.fieldAttributes.keys()):
            attribute_field = self.fieldAttributes[attribute_name]
            if 'w' in self.filteredAttributes.get(attribute_name, ''):
                continue
            child_name, child = self.writeAttribute(attribute_field, field)
            if child is not None:
                if child_name in element:
                    element[child_name].append(child)
                else:
                    element[child_name] = child
        return name, element

    # Field attribute read and write

    def readAttribute(self, element, attributeField):
        """Read a single attribute from the given element. The attribute is of
        a type described by the given Field object.
        """
        return elementToValue(attributeField, element)

    def writeAttribute(self, attributeField, field, ignoreDefault=True):
        """Create and return a element that describes the given attribute
        field on the given field
        """

        elementName = attributeField.__name__
        attributeField = attributeField.bind(field)
        value = attributeField.get(field)

        force = (elementName in self.forcedFields)

        if ignoreDefault and value == attributeField.default:
            return elementName, None

        # The value points to another field. Recurse.
        if IField.providedBy(value):
            value_fieldType = IFieldNameExtractor(value)()
            handler = queryUtility(
                IFieldExportImportHandler,
                name=value_fieldType
            )
            if handler is None:
                return elementName, None
            return handler.write(
                value, name=None,
                type=value_fieldType,
                elementName=elementName
            )

        # For 'default', 'missing_value' etc, we want to validate against
        # the imported field type itself, not the field type of the attribute
        if elementName in self.fieldTypeAttributes or \
                elementName in self.nonValidatedfieldTypeAttributes:
            attributeField = field

        return valueToElement(
            attributeField,
            value,
            name=elementName,
            force=force
        )


class JSONDictHandler(JSONBaseHandler):

    """Special handling for the Dict field, which uses Attribute instead of
    Field to describe its key_type and value_type.
    """

    def __init__(self, klass):
        super(JSONDictHandler, self).__init__(klass)
        self.fieldAttributes['key_type'] = zope.schema.Field(
            __name__='key_type',
            title=u"Key type"
        )
        self.fieldAttributes['value_type'] = zope.schema.Field(
            __name__='value_type',
            title=u"Value type"
        )


class JSONObjectHandler(JSONBaseHandler):

    """Special handling for the Object field, which uses Attribute instead of
    Field to describe its schema
    """

    # We can't serialise the value or missing_value of an object field.

    filteredAttributes = JSONBaseHandler.filteredAttributes.copy()
    filteredAttributes.update({'default': 'w', 'missing_value': 'w'})

    def __init__(self, klass):
        super(JSONObjectHandler, self).__init__(klass)

        # This is not correctly set in the interface
        self.fieldAttributes['schema'] = zope.schema.InterfaceField(
            __name__='schema'
        )


class JSONChoiceHandler(JSONBaseHandler):

    """Special handling for the Choice field
    """

    filteredAttributes = JSONBaseHandler.filteredAttributes.copy()
    filteredAttributes.update(
        {'vocabulary': 'w',
         'values': 'w',
         'source': 'w',
         'vocabularyName': 'rw'
         }
    )

    def __init__(self, klass):
        super(JSONChoiceHandler, self).__init__(klass)

        # Special options for the constructor. These are not automatically
        # written.

        self.fieldAttributes['vocabulary'] = \
            zope.schema.TextLine(
                __name__='vocabulary',
                title=u"Named vocabulary"
        )

        self.fieldAttributes['values'] = \
            zope.schema.List(
                __name__='values',
                title=u"Values",
                value_type=zope.schema.Text(title=u"Value")
        )

        # XXX: We can't be more specific about the schema, since the field
        # supports both ISource and IContextSourceBinder. However, the
        # initialiser will validate.
        self.fieldAttributes['source'] = \
            zope.schema.Object(
                __name__='source',
                title=u"Source",
                schema=Interface
        )

    def readAttribute(self, element, attributeField):
        if element.tag == 'values':
            if any([child.get('key') for child in element]):
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
        return super(JSONChoiceHandler, self)._constructField(attributes)

    def write(self, field, name, type, elementName='field'):

        element = super(JSONChoiceHandler, self).write(
            field, name, type, elementName)

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
        elif field.vocabularyName is None \
                and IVocabularyTokenized.providedBy(field.vocabulary):
            value = []
            for term in field.vocabulary:
                if (not isinstance(term.value, (str, unicode), )
                        or term.token != term.value.encode('unicode_escape')):
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
                _pair = lambda v: v if len(v) == 2 else (v[0],) * 2
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
