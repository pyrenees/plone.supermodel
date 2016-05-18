# -*- coding: utf-8 -*-
from lxml import etree
from plone.supermodel.interfaces import SECURITY_NAMESPACE
from plone.supermodel.interfaces import SECURITY_PREFIX
from plone.supermodel.interfaces import READ_PERMISSIONS_KEY
from plone.supermodel.interfaces import WRITE_PERMISSIONS_KEY
from plone.supermodel.parser import IFieldMetadataHandler
from plone.supermodel.utils import ns
from zope.component import provideAdapter
from zope.interface import implementer
from zope.interface import Interface
from zope.interface.interface import InterfaceClass


@implementer(IFieldMetadataHandler)
class SecuritySchema(object):
    """Support the security: namespace in model definitions.
    """

    namespace = SECURITY_NAMESPACE
    prefix = SECURITY_PREFIX

    def read(self, fieldNode, schema, field):
        name = field.__name__

        read_permission = fieldNode.get(ns('read-permission', self.namespace))
        write_permission = fieldNode.get(
            ns('write-permission', self.namespace)
        )

        read_permissions = schema.queryTaggedValue(READ_PERMISSIONS_KEY, {})
        write_permissions = schema.queryTaggedValue(WRITE_PERMISSIONS_KEY, {})

        if read_permission:
            read_permissions[name] = read_permission
            schema.setTaggedValue(READ_PERMISSIONS_KEY, read_permissions)

        if write_permission:
            write_permissions[name] = write_permission
            schema.setTaggedValue(WRITE_PERMISSIONS_KEY, write_permissions)

    def write(self, fieldNode, schema, field):
        name = field.__name__

        read_permission = schema.queryTaggedValue(
            READ_PERMISSIONS_KEY, {}
        ).get(name, None)
        write_permission = schema.queryTaggedValue(
            WRITE_PERMISSIONS_KEY,
            {}
        ).get(name, None)

        if read_permission:
            fieldNode.set(
                ns('read-permission', self.namespace),
                read_permission
            )
        if write_permission:
            fieldNode.set(
                ns('write-permission', self.namespace),
                write_permission
            )