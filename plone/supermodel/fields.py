# -*- coding: utf-8 -*-
import plone.supermodel.exportimport
import zope.schema

# Field import/export handlers

XMLBytesHandler = plone.supermodel.exportimport.XMLBaseHandler(zope.schema.Bytes)
XMLASCIIHandler = plone.supermodel.exportimport.XMLBaseHandler(zope.schema.ASCII)
XMLBytesLineHandler = plone.supermodel.exportimport.XMLBaseHandler(
    zope.schema.BytesLine)
XMLASCIILineHandler = plone.supermodel.exportimport.XMLBaseHandler(
    zope.schema.ASCIILine)
XMLTextHandler = plone.supermodel.exportimport.XMLBaseHandler(zope.schema.Text)
XMLTextLineHandler = plone.supermodel.exportimport.XMLBaseHandler(
    zope.schema.TextLine)
XMLBoolHandler = plone.supermodel.exportimport.XMLBaseHandler(zope.schema.Bool)
XMLIntHandler = plone.supermodel.exportimport.XMLBaseHandler(zope.schema.Int)
XMLFloatHandler = plone.supermodel.exportimport.XMLBaseHandler(zope.schema.Float)
XMLDecimalHandler = plone.supermodel.exportimport.XMLBaseHandler(zope.schema.Decimal)
XMLTupleHandler = plone.supermodel.exportimport.XMLBaseHandler(zope.schema.Tuple)
XMLListHandler = plone.supermodel.exportimport.XMLBaseHandler(zope.schema.List)
XMLSetHandler = plone.supermodel.exportimport.XMLBaseHandler(zope.schema.Set)
XMLFrozenSetHandler = plone.supermodel.exportimport.XMLBaseHandler(
    zope.schema.FrozenSet)
XMLPasswordHandler = plone.supermodel.exportimport.XMLBaseHandler(
    zope.schema.Password)
XMLDictHandler = plone.supermodel.exportimport.XMLDictHandler(zope.schema.Dict)
XMLDatetimeHandler = plone.supermodel.exportimport.XMLBaseHandler(
    zope.schema.Datetime)
XMLDateHandler = plone.supermodel.exportimport.XMLBaseHandler(zope.schema.Date)
XMLSourceTextHandler = plone.supermodel.exportimport.XMLBaseHandler(
    zope.schema.SourceText)
XMLURIHandler = plone.supermodel.exportimport.XMLBaseHandler(zope.schema.URI)
XMLIdHandler = plone.supermodel.exportimport.XMLBaseHandler(zope.schema.Id)
XMLDottedNameHandler = plone.supermodel.exportimport.XMLBaseHandler(
    zope.schema.DottedName)
XMLInterfaceFieldHandler = plone.supermodel.exportimport.XMLBaseHandler(
    zope.schema.InterfaceField)
XMLObjectHandler = plone.supermodel.exportimport.XMLObjectHandler(zope.schema.Object)
XMLChoiceHandler = plone.supermodel.exportimport.XMLChoiceHandler(zope.schema.Choice)

JSONBytesHandler = plone.supermodel.exportimport.JSONBaseHandler(zope.schema.Bytes)
JSONASCIIHandler = plone.supermodel.exportimport.JSONBaseHandler(zope.schema.ASCII)
JSONBytesLineHandler = plone.supermodel.exportimport.JSONBaseHandler(
    zope.schema.BytesLine)
JSONASCIILineHandler = plone.supermodel.exportimport.JSONBaseHandler(
    zope.schema.ASCIILine)
JSONTextHandler = plone.supermodel.exportimport.JSONBaseHandler(zope.schema.Text)
JSONTextLineHandler = plone.supermodel.exportimport.JSONBaseHandler(
    zope.schema.TextLine)
JSONBoolHandler = plone.supermodel.exportimport.JSONBaseHandler(zope.schema.Bool)
JSONIntHandler = plone.supermodel.exportimport.JSONBaseHandler(zope.schema.Int)
JSONFloatHandler = plone.supermodel.exportimport.JSONBaseHandler(zope.schema.Float)
JSONDecimalHandler = plone.supermodel.exportimport.JSONBaseHandler(zope.schema.Decimal)
JSONTupleHandler = plone.supermodel.exportimport.JSONBaseHandler(zope.schema.Tuple)
JSONListHandler = plone.supermodel.exportimport.JSONBaseHandler(zope.schema.List)
JSONSetHandler = plone.supermodel.exportimport.JSONBaseHandler(zope.schema.Set)
JSONFrozenSetHandler = plone.supermodel.exportimport.JSONBaseHandler(
    zope.schema.FrozenSet)
JSONPasswordHandler = plone.supermodel.exportimport.JSONBaseHandler(
    zope.schema.Password)
JSONDictHandler = plone.supermodel.exportimport.JSONDictHandler(zope.schema.Dict)
JSONDatetimeHandler = plone.supermodel.exportimport.JSONBaseHandler(
    zope.schema.Datetime)
JSONDateHandler = plone.supermodel.exportimport.JSONBaseHandler(zope.schema.Date)
JSONSourceTextHandler = plone.supermodel.exportimport.JSONBaseHandler(
    zope.schema.SourceText)
JSONURIHandler = plone.supermodel.exportimport.JSONBaseHandler(zope.schema.URI)
JSONIdHandler = plone.supermodel.exportimport.JSONBaseHandler(zope.schema.Id)
JSONDottedNameHandler = plone.supermodel.exportimport.JSONBaseHandler(
    zope.schema.DottedName)
JSONInterfaceFieldHandler = plone.supermodel.exportimport.JSONBaseHandler(
    zope.schema.InterfaceField)
JSONObjectHandler = plone.supermodel.exportimport.JSONObjectHandler(zope.schema.Object)
JSONChoiceHandler = plone.supermodel.exportimport.JSONChoiceHandler(zope.schema.Choice)
