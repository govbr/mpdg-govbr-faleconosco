# -*- coding: utf-8 -*-

from five import grok
from plone import api

from Products.CMFCore.interfaces import ISiteRoot

grok.templatedir('templates')


class UsuariosView(grok.View):
    """ View para adicionar usuarios ao encaminhar
    """

    grok.name('usuarios')
    grok.require('zope2.View')
    grok.context(ISiteRoot)

    def usuarios(self):
        usuarios = api.user.get_users(groupname="adm-fale-conosco")
        logged_user = api.user.get_current().id
        result = []
        for usuario in usuarios:
            user_id = usuario.getId()
            if logged_user != user_id:
                result.append(
                    dict(nome=usuario.getProperty('fullname'),
                         email=usuario.getProperty('email'),
                         user_id=user_id)
                )
        return result
