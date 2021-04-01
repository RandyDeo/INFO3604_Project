// Section 3 Duplication Code
$(document).ready(function() {
    $('#add').click(function() {
        var num     = $('.clonedSection').length;
        var newNum  = new Number(num + 1);

        var newSection = $('#clonedSection' + num).clone().attr('id', 'clonedSection' + newNum);

        newSection.children(':first').children(':first').attr('id', 'task_name' + newNum).attr('name', 'task_name' + newNum);
        newSection.children(':nth-child(2)').children(':first').attr('id', 'task_descript' + newNum).attr('name', 'task_descript' + newNum);
        newSection.children(':nth-child(3)').children(':first').attr('id', 'team_member' + newNum).attr('name', 'team_member' + newNum);


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

//Section 2 Duplication Code
