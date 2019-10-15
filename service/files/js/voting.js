$("#select_btn button").click(function(e){
    if($(e.target).hasClass('btn-primary')){
        var vote_gp = $(e.target).html().replace('Grp', 'Group');
        var disable_gp = 'select_' + vote_gp.toLowerCase().replace(' ', '_')

        $("#vote_submit_btn").attr('disabled', false).removeClass('btn-secondary').addClass('btn-primary');
        $(".selectors").attr('disabled', false);
        var all_switch = $(".selectors");
        for (var i = 0; i < all_switch.length; i++){
            all_switch[i].options[0].selected = true;
        }
        $("#"+disable_gp).attr('disabled', true);
        $("#group_name").val(vote_gp);
        $("#group_id").html(vote_gp);
    }
});

$(".selectors").change(function(e){
    var temp_val = $(e.target).val();
    var all_switch = $(".selectors");
    var match = 0;
    if (temp_val != ''){
        for (var i = 0; i < all_switch.length; i++){
            if($(all_switch[i]).val() == temp_val){
                match++;
            }
        } 
    }
    if(match > 1){
        $(e.target).val('');
        alert('Please do not select duplicate options');
    }
});

$('form').submit(function(e) {
    var all_switch = $(".selectors");
    var selected_list = [];
    for (var i = 0; i < all_switch.length; i++){
        if($(all_switch[i]).val() != ''){
            selected_list.push(parseInt($(all_switch[i]).val()));
        }
    }
    
    if (selected_list.length == 0){
        alert('Please select at least 1 options');
        e.preventDefault();
        return false;
    }else if (Math.max(...selected_list) > selected_list.length) {
        alert('Please rank start from 1');
        e.preventDefault();
        return false;
    }
});