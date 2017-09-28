mpdg.govbr.faleconosco: Fale Conosco
====================================


[![Coverage Status](https://coveralls.io/repos/github/Samuelbsb/mpdg.govbr.faleconosco/badge.svg?branch=master)](https://coveralls.io/github/Samuelbsb/mpdg.govbr.faleconosco?branch=master) [![Build Status](https://travis-ci.org/Samuelbsb/mpdg.govbr.faleconosco.svg?branch=master)](https://travis-ci.org/Samuelbsb/mpdg.govbr.faleconosco)

Introdução
-----------

Este pacote provê um conjunto de funcionalidades para gerenciar mensagens do Fale Conosco do portal. Dentre as principais:

- Confirmação da mensagem através de token enviado por email;
- Painel administrativo para gerenciamento das mensagens;
- Busca simples e avançada;
- Possibilidade de encaminhar a mensagem para usuários responsáveis por outros setores;
- Categorização e arquivamento de mensagens;
- Estatísticas de mensagens respondidas, em aberto, em atraso e alerta;
- Mensagens de notificação de email customizadas;

Compatibilidade
---------------

O pacote foi testado em versões do Plone 4.x

Instalação
------------

Para habilitar a instalação deste produto em um ambiente que utilize o
buildout:

1. Editar o arquivo buildout.cfg (ou outro arquivo de configuração) e
   adicionar o pacote `mpdg.govbr.faleconosco` à lista de eggs da instalação:

        [buildout]
        ...
        eggs =
            mpdg.govbr.faleconosco

2. Após alterar o arquivo de configuração é necessário executar
   ''bin/buildout'', que atualizará sua instalação.

3. Reinicie o Plone

4. Acesse o painel de controle e instale o produto
**mpdg.govbr.faleconosco: Fale Conosco**.

Estado deste pacote
---------------------

O **mpdg.govbr.faleconosco** está em constante atualização e está em sua primeira versão estável aberta. O pacote ainda não possui testes automatizados mas estamos trabalhando para aumentar sua cobertura de testes e assim fornecer uma experiência ainda melhor. Você está convidado a ajudar!

Uso
---

Após instalação, será criado na raiz do Plone site uma pasta chamada "Fale Conosco" (/fale-conosco), essa pasta é o local onde serão salvas as mensagens enviadas pelo formulário.

O formulário de contato do Fale Conosco estará disponível em /fale-conosco/@@fale-conosco/

Após o envio da mensagem o usuário deverá clicar no link de confirmação enviado para o email fornecido no momento do contato.

Na instalação do produto é criado um portlet de navegação com links para "Perguntas Frequentes" e o "Painel de Administração do Fale Conosco".

Nas perguntas frequentes você pode criar quantas 'Páginas' desejar, cada uma para uma pergunta frequente. Se publicadas, elas serão exibidas ao lado do formulário do Fale Conosco que o usuário tem acesso.

O Painel de Administração do Fale Conosco é acessível apenas para os usuários que estiverem no grupo "adm-fale-conosco", criado também automaticamente na instalação do produto.

Também deve ser configurado o Administrador do Fale Conosco, isso pode ser feito no painel de controle, na opção "mpdg.govbr.faleconosco: Fale Conosco". Esse usuário é o primeiro que receberá as mensagens do Fale, e poderá responder diretamente ao usuário ou encaminhar a mensagem para algum usuário do grupo "adm-fale-conosco".
