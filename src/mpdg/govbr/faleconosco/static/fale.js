    $(document).ready(function(){
        parametros = window.location.href.slice(window.location.href.indexOf('?') + 1).split('&')
        for(var i = 0; i<parametros.length; i++) {
            if (parametros[i].split('=')[0].match('msg')) {
                uid = parametros[i].split('=')[1]
            } else {
                uid = null;
            }
        }

        if (uid) {
            $('#' + uid + '.fale-mensagens').show();
        }

        $(document).on('click', '.fale-mais-mensagem a', function(){
            $(this).parent().parent().next('.fale-mensagens').toggle('slow');
            return false;
        });

        // $(document).on('click', '#fale-selecionar', function(){
        //     $('.fale-select').each(function() {
        //         this.checked = true;
        //     });
        //     return false;
        // });

        $('#marcartabela').change(function(){
            var estado = $(this).is(":checked");
            $('.fale-select').each(function() {
                this.checked = estado;
            });
            return false;
        });



        // $('#fale-desmarcar').click(function(){
        //     $('.fale-select').each(function() {
        //         this.checked = false;
        //     });
        //     return false;
        // });

        $(document).on('click', '#fale-mensagem-responder', function(){
//            uid = $(this).attr('href');
//            window.location = ("@@fale-conosco-admin?acao=responder&msg="+uid);
            $('.fale-mensagem-form').toggle('slow');
            $('.fale-responder-email').show();
            form = $('form[name="add-mensagem"]');
            if (form.find('input[name="estado"]').length === 0) {
                form.prepend($('<input type="hidden" name="estado" value="responder" />'));
            }
            $('.fale-mensagem-acao-responder-encaminhar').toggle('slow');
            return false;
        });

        $(document).on('click', '#fale-descartar', function(){
           $('.fale-mensagem-form').toggle('slow');
            $('.fale-responder-email').hide();
            $('.fale-encaminhar-email').hide();
            $('.fale-resgatar-email').hide();
            form = $('form[name="add-mensagem"]');
            if (form.find('input[name="estado"]').length !== 0) {
                form.remove('input[name="estado"]');
            }
            $('textarea[name="mensagem"]').val("");
            $('.fale-mensagem-acao-responder-encaminhar').toggle('slow');
            return false;
        });

        $(document).on('click', '.fale-mensagem-form-submit', function(ev){
            ev.preventDefault();
            var $this = $(this);
            var params = $this.parents('form').serialize();
            $.ajax({
                type: "POST",
                url: "@@add-mensagem",
                data: params,
                success: function() {
                    $('textarea[name="mensagem"]').val("");
                    var $form = $('form.use-ajax'),
                        $input = $form.find('input[name="submitted"]'),
                        url = $input.attr('ajax-url'),
                        ajax_id = $input.attr('ajax-id'),
                        ajax_filter = $input.attr('ajax-filter'),
                        ajax_evaljs = $input.attr('ajax-evaljs');

                    if($form) {
                        params = $form.serialize();
                        if(params){
                            params += '&'+this.name+'='+this.value;
                        }
                    }
                    if(ajax_id) {
                        $container_ajax = $('[ajax-content="'+ajax_id+'"]');
                        $.ajax({
                            url: url,
                            data: params,
                            success: function(data){
                                if(ajax_filter) {
                                    try{
                                        var dom = $.parseHTML(data);
                                    }catch (e) {
                                        var dom = $(data);
                                    }
                                    data = $('[ajax-content="'+ajax_filter+'"]', dom)
                                    if (!data || (data.length == 0)) {
                                        data = dom.filter('[ajax-content="'+ajax_filter+'"]')
                                    }
                                    data = data.contents();
                                }
                                if(ajax_evaljs) {
                                    $.get(ajax_evaljs, function(result){
                                        $.globalEval(result);
                                    });
                                }
                                $container_ajax.html(data);
                                location.reload();
                            }
                        });
                    };
                }
            });
        });

        $('a.fale-mensagem-encaminhar').prepOverlay({
            subtype: 'ajax',
            filter: '#content>*',
            formselector: 'form',
            closeselector: 'input.fale-usuario',
            config: {
                onBeforeLoad: function(event){
                    $id = event.target.ownerDocument.activeElement.id;
                    $form = $('form#' + $id);
                },
                onBeforeClose: function(event){
                    $('.fale-encaminhar-email').show();
                    $('.fale-mensagem-form').toggle('slow');
                    var $input = $('form[name="fale-usuarios-form"] :checked');
                    var $nome = $input.next().text();
                    var $userid = $input.next().next().text();
                    console.log($userid)
                    $form.find('.fale-encaminhar-email').find('.negrito').text('Encaminhar para: ' + $nome);
                    $form.find('input[name="email"]').attr('value', $input.attr('value'))
                    $form.find('input[name="nome"]').attr('value', $nome)
                    $form.prepend($('<input type="hidden" name="userid" value="' + $userid + '" />'));
                    if ($form.find('input[name=estado]').length === 0) {
                        $form.prepend($('<input type="hidden" name="estado" value="encaminhar" />'));
                    }
                    $('.fale-mensagem-acao-responder-encaminhar').toggle('slow');
                }
            }
        });
         $('a.fale-encaminhar-selecionados').click(function(e){
            e.preventDefault();
            var uids = [];
            $('input[name="fale-select"]:checked').each(function(){
                uids.push($(this).attr('value'));
            });
            if (uids.length === 0) {
                alert('Selecione alguma mensagem para ser respondida!');
                return false;
            } else {
                var target = $(this).attr('href');
                var target = target + '?uids=' + uids;
                return window.location = target;
            }
        });

        

        $('input.fale-usuario').prepOverlay({
            subtype: 'ajax',
            filter: '#content>*',
            formselector: 'form',
        });

        $('a.fale-inserir-textos').prepOverlay({
            subtype: 'ajax',
            filter: '#content>*',
            formselector: 'form',
            closeselector: 'input.fale-texto',
            config: {
                onBeforeLoad: function(event){
                    $id = event.target.ownerDocument.activeElement.id;
                    $div = $('div#' + $id);
                },
                onBeforeClose: function(event){
                    var $input = $('form[name="fale-textos-form"] :checked');
                    var $texto = $input.next().next().next().next()
                    var $textarea = $div.find('textarea[name="mensagem"]');
                    $textarea.val($texto.html())
                }
            }
        });

        $('a.fale-inserir-faq').prepOverlay({
            subtype: 'ajax',
            filter: '#content>*',
            formselector: 'form',
            closeselector: 'input.fale-texto',
            config: {
                onBeforeLoad: function(event){
                    $id = event.target.ownerDocument.activeElement.id;
                    $div = $('div#' + $id);
                },
                onBeforeClose: function(event){
                    var $input = $('form[name="fale-textos-form"] :checked');
                    var $texto = $input.next().next().next().next()
                    var $textarea = $div.find('textarea[name="mensagem"]');
                    $textarea.val($texto.html())
                }
            }
        });

        $(document).on('click', '#fale-mensagem-resgatar', function(){
//            uid = $(this).attr('href');
//            window.location = ("@@add-mensagem?acao=resgatar&msg="+uid);
            $('.fale-mensagem-form').toggle('slow');
            $('.fale-resgatar-email').show();
            form = $('form[name="add-mensagem"]');
            if (form.find('input[name=estado]').length === 0) {
                form.prepend($('<input type="hidden" name="estado" value="resgatar" />'));
            }
            $('.fale-mensagem-acao-responder-encaminhar').toggle('slow');
            return false;
        });

        $('a.fale-responder-selecionados').click(function(e){
            e.preventDefault();
            var uids = [];
            $('input[name="fale-select"]:checked').each(function(){
                uids.push($(this).attr('value'));
            });
            if (uids.length === 0) {
                alert('Selecione alguma mensagem para ser respondida!');
                return false;
            } else {
                var target = $(this).attr('href');
                var target = target + '?uids=' + uids;
                return window.location = target;
            }
        });

        // $('a.fale-inserir-textos-sel').prepOverlay({
        //     subtype: 'ajax',
        //     filter: '#content>*',
        //     formselector: 'form',
        //     closeselector: 'input.fale-texto',
        //     config: {
        //         onBeforeLoad: function(event){
        //             $id = event.target.ownerDocument.activeElement.id;
        //             $div = $('div#' + $id);
        //         },
        //         onBeforeClose: function(event){
        //             var $input = $('form[name="fale-textos-form"] :checked');
        //             var $texto = $input.next().next().next().next()
        //             var $textarea = $div.find('textarea[name="mensagem"]');
        //             $textarea.val($texto.text())
        //         }
        //     }
        // });
        $('a.fale-inserir-textos-sel').prepOverlay({
                subtype: 'ajax',
                filter: '#content>*',
                formselector: 'form',
                closeselector: 'input.fale-texto',
                cssclass: 'overlay2',
                config: {
                    onBeforeClose: function(event){
                        var input = $('form[name="fale-textos-form"] :checked').next().next().next().next();
                        // var texto = $(input);  // selected text
                        var textarea = $("#form-widgets-mensagem_ifr").contents().find("#content");
                        $(textarea).append($(input).html());

                    }
                }
            });

        $(document).on('click', '#fale-gerar-charts', function(){
            var $form = $('form.use-ajax');
            params = $form.serialize();
            if(params){
                window.location = ("@@fale-conosco-charts?" + params );
            } else {
                window.location = ("@@fale-conosco-charts");
            }
            return false;
        })
    });

    $(function() {
        $(document).on('click', '.call-refinar-busca', function(ev){
            var $this = $(this),
                    $form = $this.parents('form.form-filter');
            $ad_search = $('.busca-avancada', $form);
            if ($ad_search) {
                var sign = $('.sign', $this);
                if ($ad_search.css('display') == 'block')
                    sign.text('+');
                else
                    sign.text('-');
                $ad_search.toggle(200);
            }
        });
        $('.form-filter input[name="SearchableText"]').keypress(function(ev){
            if(ev.keyCode == 13) {
                $('.form-filter input[name= ,l  m,l,l"submitted"]').trigger('click');
            }
        });
    });

    // $(document).ready(function () {
    //     $(document).on('click', '#busca-fale-button', function(ev){
    //         ev.preventDefault();
    //         var $this = $(this),
    //                 url = $this.attr('ajax-url'),
    //                 ajax_id = $this.attr('ajax-id'),
    //                 ajax_filter = $this.attr('ajax-filter'),
    //                 ajax_evaljs = $this.attr('ajax-evaljs'),
    //                 $form = $(this).parents('form.use-ajax'),
    //                 params = '';
    //         if($form) {
    //             params = $form.serialize();
    //             if(params){
    //                 params += '&'+this.name+'='+this.value;
    //             }
    //         }
    //         if(ajax_id) {
    //             $container_ajax = $('[ajax-content="'+ajax_id+'"]');
    //             $.ajax({
    //                 url: url,
    //                 data: params,
    //                 beforeSend: function(){
    //                     console.log('oi!');
    //                     $('.carregando').show()
    //                 },
    //                 success: function(data){
    //                     if(ajax_filter) {
    //                         try{
    //                             var dom = $.parseHTML(data);
    //                         }catch (e) {
    //                             var dom = $(data);
    //                         }
    //                         data = $('[ajax-content="'+ajax_filter+'"]', dom)
    //                         if (!data || (data.length == 0)) {
    //                             data = dom.filter('[ajax-content="'+ajax_filter+'"]')
    //                         }
    //                         data = data.contents();
    //                     }
    //                     if(ajax_evaljs) {
    //                         $.get(ajax_evaljs, function(result){
    //                             $.globalEval(result);
    //                         });
    //                     }
    //                     $container_ajax.html(data);
    //                 },
    //                 complete: function(){
    //                     console.log('hide');
    //                     $('.carregando').hide();
    //                 }
    //             });
    //         }
    //     });
    //     $("input[type='date']").dateinput({ format: 'dd/mm/yyyy' });
    // });
