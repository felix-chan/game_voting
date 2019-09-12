$("#select_btn button").click(function(e){
    if($(e.target).hasClass('btn-primary')){
        var vote_gp = $(e.target).html().replace('Grp', 'Group');
        var disable_gp = 'select_' + vote_gp.toLowerCase().replace(' ', '_')

        $("#vote_submit_btn").attr('disabled', false).removeClass('btn-secondary').addClass('btn-primary');
        $(".custom-control-input").attr('disabled', false);
        var all_switch = $(".custom-control-input");
        for (var i = 0; i < all_switch.length; i++){
            all_switch[i].checked = false;
        }
        $("#"+disable_gp).attr('disabled', true);
        $("#group_name").val(vote_gp);
        $("#group_id").html(vote_gp);
    }
});

$(".custom-control-input").click(function(e){
    if ($(".custom-control-input:checked").length > 3){
        alert('At most 3 options');
        e.target.checked = false;
    }
});