
$(document).ready(function () {
    
    $(document).on('click', 'a[ajax-id], input[ajax-id]', function(ev){
        ev.preventDefault();
        ev.stopImmediatePropagation();
        
        var $this = $(this),
            url = $this.attr('ajax-url'),
            ajax_id = $this.attr('ajax-id'),
            ajax_filter = $this.attr('ajax-filter'),
            ajax_evaljs = $this.attr('ajax-evaljs'),
            $form = $(this).parents('form.use-ajax'),
            params = '';
        
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
                async: true,
                // beforeSend: function(){
                //         $('.carregando').show()
                //     },
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
                    if ($('table.tablesorter').length >= 1) {
                        $('table.tablesorter').tablesorter();
                    }

                },
                // complete: function(){
                //         $('.carregando').hide();
                //     }
            });
        }
    return false;
    });
});

