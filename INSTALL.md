mpdg.govbr.faleconosco
================

Arquitetura dos portais em produção
-----------------------------------

Antes de efetuar a instalação do produto é importante um entendimento geral da [arquitetura](https://git.planejamento.gov.br/plone/portal-docs/blob/desenvolvimento/documentos/arquitetura.md) dos portais em produção.

Como instalar
-------------

> **Obs**: Todos os comandos abaixo devem ser efetuados com o usuário 'plone'

Acessar o diretório onde o Plone está instalado

```
$ cd /opt/zope/zeocluster
```

Parar todas as instâncias

```
$ ./bin/plonectl stop
```

## Instalação/Atualização

Acessar o diretório 'src' onde os produtos desenvolvidos são instalados:

```
$ cd /opt/zope/zeocluster/src/
```

### Instalação

Caso o produto ainda **não esteja instalado** no portal, nós devemos inseri-lo em "src/" e criar as referências no arquivo `buildout.cfg`, conforme passos a seguir:

Efetuar o clone do produto no gitlab

```
git clone http://git.planejamento.gov.br/plone/mpdg-govbr-faleconosco.git mpdg.govbr.faleconosco
```

> **Obs**: Se você estiver em ambiente de **desenvolvimento/homologação**, deve mudar a branch para a adequada:

```
$ cd mpdg.govbr.faleconosco
$ git checkout -b desenvolvimento origin/desenvolvimento
```

Voltar para o diretório raiz da instalação do Plone

```
$ cd /opt/zope/zeocluster
```

Editar o arquivo `buildout.cfg`

```
$ vim buildout.cfg
```

Dentro da seção `[buildout]` navegar até a linha 'eggs =' e inserir o nome do produto abaixo dos demais

> **Obs**: Sempre utilizar 'quatro espaços' ao invés de 'tab' quando estiver
identando linhas dentro do buildout

    eggs =
        ...
        mpdg.govbr.faleconosco

Fazer o mesmo em 'develop ='

    develop =
        ...
        src/mpdg.govbr.faleconosco

Salvar e fechar o arquivo.

```
./bin/buildout -Nv
```

### Atualização

Se o produto **já está instalado e versionado** precisaremos apenas acessar o diretório do produto e atualizar seu conteúdo através do git, conforme passos a seguir:

```
$ cd mpdg.govbr.faleconosco
$ git pull
```

Voltar para o diretório raiz da instalação do Plone

```
$ cd /opt/zope/zeocluster
```

Iniciar as instâncias

```
$ ./bin/plonectl start
```

Se for necessário (re)instalar o produto, acessar a `ZMI (/manage) > portal_quickinstaller` ou o `Painel de controle (/plone_control_panel) > Complementos` e efetuar as ações.
