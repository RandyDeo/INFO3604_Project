$(document).ready(function() {
    $('#add').click(function() {
        var num     = $('.clonedSection').length;
        var newNum  = new Number(num + 1);

        var newSection = $('#clonedSection' + num).clone().attr('id', 'clonedSection' + newNum);

        newSection.children(':first').children(':first').attr('id', 'proj_name' + newNum).attr('name', 'proj_name' + newNum);
        newSection.children(':nth-child(2)').children(':first').attr('id', 'proj_descript' + newNum).attr('name', 'proj_descript' + newNum);
        newSection.children(':nth-child(3)').children(':first').attr('id', 'activities' + newNum).attr('name', 'activities' + newNum);


        $('.clonedSection').last().append(newSection)

        $('#delete').attr('disabled','');

        if (newNum == 5)
            $('#add').attr('disabled','disabled');
    });



    $('#delete').click(function() {
        var num = $('.clonedSection').length; // how many "duplicated" input fields we currently have
        $('#clonedSection' + num).remove();     // remove the last element

        // enable the "add" button
        $('#add').attr('disabled','');

        // if only one element remains, disable the "remove" button
        if (num-1 == 1)
            $('#delete').attr('disabled','disabled');
    });

    $('#delete').attr('disabled','disabled');
});
