# -*- coding: utf-8 -*-
"""Module where all interfaces, events and exceptions live."""

from zope.publisher.interfaces.browser import IDefaultBrowserLayer
from zope.interface import Interface


class IMpdgGovbrFaleconoscoLayer(IDefaultBrowserLayer):
    """Marker interface that defines a browser layer."""

class IFaleConosco(Interface):
    """ interface para o conteudo FaleConosco

    """

class IHistorico(Interface):
    """ interface para o conteudo Historico
    """

class IMensagem(Interface):
	""" interface para o conteudo Mensagem 
	"""

class IAssunto(Interface):
    """ interface para o conteudo Assunto
    """