$(function () {
    $('#generate').click(function () {
        const code = $('#code_textarea').val()
        console.log(code)
        $.ajax({
            url: "/save_code",
            type: "post",
            data: {
                "code":code
            },
            success: function (res) {
                console.log(res)
                $('#test').val(res)
            }
        })
    })
})