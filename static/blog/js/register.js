$(function () {

    $('#avatar').change(function () {

        //获取用户选中文件的对象
        var file_obj = $(this)[0].files[0];

        //获取文件的路径
        var file_url = new FileReader();
        file_url.readAsDataURL(file_obj);//读取文件的路径

        //修改img的src属性，src=文件对象对应的路径
        file_url.onload = function () {               //在上面读取文件完成之后执行修改，否则无法显示
            $('#avatar_img').attr('src', file_url.result)
        }
    });

    //ajax提交formdata数据
    $('#reg_btn').click(function () {
        var form_data = new FormData();
        // form_data.append("user", $("#id_name").val());
        // form_data.append("pwd", $("#id_pwd").val());
        // form_data.append("re_pwd", $("#id_re_pwd").val());
        // form_data.append("email", $("#id_email").val());
        // form_data.append("avatar", $("#avatar")[0].files[0]);
        // form_data.append("csrfmiddlewaretoken", $("[name='csrfmiddlewaretoken']").val());


        //优化
        var form_list = $('#form').serializeArray();//得到一个列表[{},{}]
        //console.log(form_list);

        //循环列表，function（索引，字典）
        $.each(form_list, function (index, data) {
            form_data.append(data.name, data.value)
        });
        //单独添加文件
        form_data.append("avatar", $('#avatar')[0].files[0]);

        $.ajax({
            url: "",
            type: "post",
            contentType: false,
            processData: false,
            data: form_data,
            success: function (data) {
                //console.log(data);

                if (data.user) {
                    //注册成功
                    location.href = "/login/"
                }
                else {
                    //注册失败
                    //console.log(data.msg);

                    //显示错误信息

                    $('.error').html('');//清除错误信息
                    $('.form-group').removeClass('has-error');

                    $.each(data.msg, function (field, error_list) {
                        //显示全局错误信息__all__
                        if (field === "__all__") {
                            $('#id_re_pwd').next().html(error_list[0]).parent().addClass('has-error')
                        }

                        $("#id_" + field).next().text(error_list[0]);
                        $("#id_" + field).parent().addClass('has-error ');

                    })

                }
            }

        })
    })
});