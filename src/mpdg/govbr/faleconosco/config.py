# -*- coding: utf-8 -*-

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


EMAIL_FALE = "<p> Obrigado %s pelo seu contato! </p> \n"\
              "<b>Sua mensagem:</b>\n"\
              "<ul>\n"\
              "<li>Título: <i> %s </i></li>\n"\
              "<li>Mensagem: <i> %s </i> </li>\n"\
              "</ul>\n"\
              "\n"\
              "<p> <b>Por favor, confirme o envio da sua mensagem no e-mail %s . Após sua confirmação, a sua mensagem será enviada para os responsáveis do Sítio do Governo Eletrônico.</p> \n"\
              "Para confirmar esta mensagem, por favor, acesse o link  %s"