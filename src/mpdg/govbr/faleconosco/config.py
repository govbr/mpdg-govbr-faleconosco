# -*- coding: utf-8 -*-
from Products.CMFPlone import interfaces as plone_interfaces
from zope.interface import implementer

PROJECTNAME = 'mpdg.govbr.faleconosco'

ADD_PERMISSIONS = {
    'FaleConosco': 'mpdg.govbr.faleconosco: Add FaleConosco',
    'Historico': 'mpdg.govbr.faleconosco: Add Historico',
    'Mensagem': 'mpdg.govbr.faleconosco: Add Mensagem',
}


DIAS_PRAZO = 2
DIAS_ALERTA= 5
DIAS_ATRASO = 6

KEY_CONFIRMA ='mpdg.govbr.faleconosco.confrma'


EMAIL_FALE = u"<p> Obrigado [nome] pelo seu contato! </p> \n"\
              u"<b>Sua mensagem: </b>\n"\
              u"<ul>\n"\
              u"<li>Título: <i> [assunto] </i></li>\n"\
              u"<li>Mensagem: <i> [mensagem] </i> </li>\n"\
              u"</ul>\n"\
              u"\n"\

EMAIL_FALE_LINK = u"\n"\
                  u"<p>Para confirmar esta mensagem, por favor, acesse o link %s</p>"\
                  u"<p>Após sua confirmação, a sua mensagem será enviada para os responsáveis do site.</p> \n"\


EMAIL_FALE_ASSINATURA = u"<p>Atenciosamente,</p>"\
                        u'<p>Equipe do Governo Digital.</p>'


@implementer(plone_interfaces.INonInstallable)
class HiddenProfiles(object):

    def getNonInstallableProfiles(self):
        return [
            u'mpdg.govbr.faleconosco:testing',
        ]
