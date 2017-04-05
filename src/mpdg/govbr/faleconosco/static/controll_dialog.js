$(document).ready( function() {
    $( ".dialog" ).dialog({
        resizable: false,
        autoOpen: false,
        modal: true,
        buttons: {
            'Cancelar': function() {
                $(this).dialog('close');
            }
        }
    });
    $(".categorizar-msg").click(function(e) {
        e.preventDefault();
        var target = $(this).attr("data-dialog");
        $("#"+target).dialog( "open" );
    });
    $( "#cancel" ).click(function(e) {
        e.preventDefault();
        $("#dialog").dialog( "close" );
    });
    $('.tags').tagsInput({width: 'auto'});
} );
