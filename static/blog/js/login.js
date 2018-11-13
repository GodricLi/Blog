$(function () {

    //验证码刷新
    $('#valid_code_img').click(function () {
        $(this)[0].src += "?"
    });

    //ajax事件校验验证码
    $('#login_btn').click(function () {

        $.ajax({
            url: "",
            type: "post",
            data: {
                user: $('#user').val(),
                pwd: $('#pwd').val(),
                valid_code: $('#valid_code').val(),
                csrfmiddlewaretoken: $("[name='csrfmiddlewaretoken']").val()
            },
            success: function (data) {
                console.log(data);

                if (data.user) {
                    //前端跳转
                    location.href = '/index/'
                }
                else {
                    $('.error').text(data.msg).css({'color': 'red', 'margin-left': '10px'});

                    setTimeout(function () {
                        $('.error').text('')
                    }, 2000)
                }

            }
        })
    });
});
