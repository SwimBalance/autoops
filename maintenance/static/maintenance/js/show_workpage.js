/**
 * Created by d046532 on 2017/7/11.
 */

//加载主页相关的内容
$(function () {
    $("#home").click(function () {
        $("#workpage").empty().load("/static/maintenance/html/workpage.html #home_workpage");
    })
});


//加载服务启停功能的内容
$(function () {
    // $(".disabled").click(function (event) {
    //     event.preventDefault();
    // });
    $("ul[id='servicemgr'] li").click(function () {
        <!-- 导入workPage-->
        if (this.id == 'toms') {
            $("#workpage").empty().load("/static/maintenance/html/workpage.html #tom_workpage");
            $("#modal_page").empty().load("/static/maintenance/html/modal.html #myTomcatModal");
            $.ajax({
                type: "GET",
                url: "./../tomcatData/",
                datatype: 'json',
                data: {page: 1},
                success: function (datas) {
                    loadtomcatdata(datas)
                }
            });
        } else if (this.id == 'oras') {
            $("#workpage").empty().load("/static/maintenance/html/workpage.html #ora_workpage");
            $("#modal_page").empty().load("/static/maintenance/html/modal.html #myOracleModal");
            $.ajax({
                type: "GET",
                url: "./../oracleData/",
                datatype: 'json',
                data: {page: 1},
                success: function (datas) {
                    loadoracledata(datas)
                }
            })
        } else if (this.id == 'apache') {
            $("#workpage").empty().load("/static/maintenance/html/workpage.html #apache_workpage");
            $("#modal_page").empty().load("/static/maintenance/html/modal.html #myApacheModal");
            $.ajax({
                type: "GET",
                url: "./../apacheData/",
                data: {page: 1},
                datatype: 'json',
                success: function (datas) {
                    loadapachedata(datas)
                }
            })
        } else if (this.id == 'nginx') {
            $("#workpage").empty().load("/static/maintenance/html/workpage.html #nginx_workpage");
            $("#modal_page").empty().load("/static/maintenance/html/modal.html #myNginxModal");
            $.ajax({
                type: "GET",
                url: "./../nginxData/",
                data: {page: 1},
                datatype: 'json',
                success: function (datas) {
                    loadnginxdata(datas)
                }
            })
        } else if (this.id == 'mysql') {
            $("#workpage").empty().load("/static/maintenance/html/workpage.html #mysql_workpage");
            $("#modal_page").empty().load("/static/maintenance/html/modal.html #myMysqlModal");
            $.ajax({
                type: "GET",
                url: "./../mysqlData/",
                data: {page: 1},
                datatype: 'json',
                success: function (datas) {
                    loadmysqldata(datas)
                }
            })
        }
    });
});

// 针对tomcat服务器的操作
function opt_tomcat(obj) {
    //进度条当前宽度
    var count = 0;
    var widthcount = 0;
    //定时器变量
    var timer1;
    //获取modal的body
    var tomcat_mes = $("#tomcat_message");
    //获取button上记录的该操作的超时时间
    var opstime = obj.value;
    //初始化进度条为0
    $('#progstatus').css('width', '0%');
    tomcat_mes.empty().append("正在玩命操作，预计" + opstime + "秒内完成！");
    //点击button后，将当前button标记为disabled的状态
    $(obj).addClass('disabled');
    //弹出modal的关闭按钮也变为disabled状态
    $("#messagemodal").prop('disabled', true);
    var id = obj.id;
    var action = obj.name;
    $.ajax({
        type: 'Get',
        url: './../operation/tomcat',
        data: {'id': id, 'action': action},
        //ajax调用后触发刷新进度条的任务
        beforSend: showprogress(),
        success: function (data) {
            tomcat_mes.empty().append(data['message']);
            //更新状态
            if (data['status'] == '101') {
                $(obj).parent().prevAll('.status').children('span').attr({
                    'class': 'glyphicon glyphicon-ok-sign',
                    'title': 'Tomcat正常运行'
                });
                $(obj).parent().prevAll('.status').children('span').attr({'title': 'Tomcat正常运行'}).tooltip('fixTitle');
            } else if (data['status'] == '102' || data['status'] == '104' || data['status'] == '105') {
                $(obj).parent().prevAll('.status').children('span').attr({'class': 'glyphicon glyphicon-exclamation-sign'});
                $(obj).parent().prevAll('.status').children('span').attr({'title': 'Tomcat异常，请联系管理员'}).tooltip('fixTitle');
            } else if (data['status'] == '103') {
                $(obj).parent().prevAll('.status').children('span').attr({'class': 'glyphicon glyphicon-remove-sign'});
                $(obj).parent().prevAll('.status').children('span').attr({'title': 'Tomcat已关闭'}).tooltip('fixTitle');
            }
            $(obj).removeClass('disabled');
            $("#messagemodal").removeAttr("disabled");
            //后台调用成功，停止定时器，同时将进度条刷新到100%
            clearInterval(timer1);
            $('#progstatus').css("width", "100%");
        }
    });
    //启动定时器，根据超时时间刷新进度条的状态
    function showprogress() {
        //定义一个定时器，开始刷新进度条
        timer1 = setInterval(function () {
            count = count + 1;
            //alert(count);
            widthcount = (count / opstime) * 100;
            $('#progstatus').css("width", widthcount + "%");
            //如果达到超时时间，停止定时器
            if (parseInt(count) == parseInt(opstime)) {
                clearInterval(timer1);
            }
        }, 1000);
    }
}
// tomcat分页实现
function createTomcatPage(obj) {
    var page_number = '';
    var to_page = obj.value;
    var current_page = $('#curnpage').text();
    if (to_page == '0') {
        if (current_page == '1') {
            page_number = current_page
        } else {
            page_number = parseInt(current_page) - 1
        }
    } else if (to_page == '9999') {
        page_number = parseInt(current_page) + 1;
    }
    $.ajax({
        type: "GET",
        url: "./../tomcatData/",
        datatype: 'json',
        data: {'page': page_number},
        success: function (datas) {
            loadtomcatdata(datas)
        }
    });
}
//导入tomcat数据
function loadtomcatdata(data) {
    //获取数据
    var datas = data['results'];
    var current_page = data['page'];
    var firstrecord = (current_page - 1) * 9 + 1;
    var lastrecord = firstrecord + datas.length - 1;
    var total = Math.ceil(data['total'] / 9);
    //跟新label标签的内容
    $('#curnpage').empty().append(current_page);
    //导入分页栏的数据
    if (current_page == 1) {
        $('.pager .previous').addClass('disabled')
    } else {
        $('.pager .previous').removeClass('disabled')
    }
    if (current_page == total) {
        $('.pager .next').addClass('disabled')
    } else {
        $('.pager .next').removeClass('disabled')
    }
    $('.pager strong:eq(0)').empty().append(current_page);
    $('.pager strong:eq(1)').empty().append(firstrecord);
    $('.pager strong:eq(2)').empty().append(lastrecord);
    $('.pager strong:eq(3)').empty().append(total);
    //导入表格内容
    var text = $('.text');
    text.empty();
    var html = '';
    for (var i = 0; i < datas.length; i++) {
        var id = datas[i]['id'];
        var ip = datas[i]['ipaddress'];
        var host = datas[i]['machine'];
        var dec = datas[i]['description'];
        var status = datas[i]['status'];
        var startwait = datas[i]['startwait'];
        var stopwait = datas[i]['stopwait'];
        var checkwait = datas[i]['checkwait'];
        html += '<tr>';
        html += '<td>' + id + '</td>';
        html += '<td class="ipaddress">' + ip + '</td>';
        html += '<td>' + host + '</td>';
        html += '<td>' + dec + '</td>';
        // html += '<td class="status">' + status + '</td>';
        //更新状态
        if (status == '101') {
            html += '<td class="status" ><span class="glyphicon glyphicon-ok-sign" aria-hidden="true" data-toggle="tooltip" title="Tomcat正常运行"></span></td>';
        } else if (status == '102' || status == '104' || status == '105') {
            html += '<td class="status" ><span class="glyphicon glyphicon-exclamation-sign" aria-hidden="true" data-toggle="tooltip" title="Tomcat异常，请联系管理员"></span></td>';
        } else if (status == '103') {
            html += '<td class="status" ><span class="glyphicon glyphicon-remove-sign" aria-hidden="true" data-toggle="tooltip" title="Tomcat已关闭"></span></td>';
        }
        html += '<td>' + '<button id=' + id + ' onclick="opt_tomcat(this)" name="check_tomcat" class="btn btn-default" data-toggle="modal" data-target="#myTomcatModal" value="' + checkwait + '">';
        html += '<span class="glyphicon glyphicon-check" aria-hidden="true"></span></button></td>';
        //html += '<td>' + '<button id=' + id + ' onclick="opt_tomcat(this)" name="start_tomcat" class="btn btn-default" data-toggle="modal" data-target="#myModal">';
        html += '<td>' + '<button id=' + id + ' onclick="opt_tomcat(this)" name="start_tomcat" class="btn btn-default" data-toggle="modal" data-target="#myTomcatModal" value="' + startwait + '">';
        html += '<span class="glyphicon glyphicon-play" aria-hidden="true"></span></button></td>';
        html += '<td>' + '<button id=' + id + ' onclick="opt_tomcat(this)" name="stop_tomcat" class="btn btn-default" data-toggle="modal" data-target="#myTomcatModal" value="' + stopwait + '">';
        html += '<span class="glyphicon glyphicon-stop" aria-hidden="true"></span></button></td>';
        // += '<td class="startwait" style="display:none" >' + startwait + '</td>';
        //html += '<td class="stopwait"  style="display:none">' + stopwait + '</td>';
        html += '</tr>';
    }
    text.append(html);
    //开启tooltip
    $(function () {
        $("[data-toggle='tooltip']").tooltip();
    });
}
//tomcat搜索栏
function searchtomcat() {

    var search_val = $('#search_tom').val();
    $.ajax({
        type: "GET",
        url: "/../searchtomcat/",
        data: {'data': search_val},
        datatype: "json",
        success: function (datas) {
            loadtomcatdata(datas);
            $('#preandnext').empty()
        }
    })
}

//加载oracle数据库相关信息--by lvshaohe
function loadoracledata(data) {
    //获取数据
    var datas = data['results'];
    var current_page = data['page'];
    var firstrecord = (current_page - 1) * 9 + 1;
    var lastrecord = firstrecord + datas.length - 1;
    var total = Math.ceil(data['total'] / 9);
    //跟新label标签的内容
    $('#curnpage').empty().append(current_page);
    //导入分页栏的数据
    if (current_page == 1) {
        $('.pager .previous').addClass('disabled')
    } else {
        $('.pager .previous').removeClass('disabled')
    }
    if (current_page == total) {
        $('.pager .next').addClass('disabled')
    } else {
        $('.pager .next').removeClass('disabled')
    }
    $('.pager strong:eq(0)').empty().append(current_page);
    $('.pager strong:eq(1)').empty().append(firstrecord);
    $('.pager strong:eq(2)').empty().append(lastrecord);
    $('.pager strong:eq(3)').empty().append(total);
    //导入表格内容
    var text = $('.text');
    text.empty();
    var html = '';
    for (var i = 0; i < datas.length; i++) {
        var id = datas[i]['id'];
        var ip = datas[i]['ipaddress'];
        var sid = datas[i]['sid'];
        var hostname = datas[i]['machine'];
        var status = datas[i]['status'];
        var startwait = datas[i]['startwait'];
        var stopwait = datas[i]['stopwait'];
        var checkwait = datas[i]['checkwait'];
        html += '<tr>';
        html += '<td>' + id + '</td>';
        html += '<td>' + ip + '</td>';
        html += '<td>' + hostname + '</td>';
        html += '<td>' + sid + '</td>';
        //更新状态
        if (status == '201') {
            html += '<td class="status" ><span class="glyphicon glyphicon-ok-sign" aria-hidden="true" data-toggle="tooltip" title="Oracle数据库正常运行"></span></td>';
        } else if (status == '202') {
            html += '<td class="status" ><span class="glyphicon glyphicon-exclamation-sign" aria-hidden="true" data-toggle="tooltip" title="Oracle数据库异常，请联系管理员"></span></td>';
        } else if (status == '203') {
            html += '<td class="status" ><span class="glyphicon glyphicon-remove-sign" aria-hidden="true" data-toggle="tooltip" title="Oracle数据库已关闭"></span></td>';
        }
        html += '<td>' + '<button id=' + id + ' onclick="opt_oracle(this)" name="check_oracle" class="btn btn-default" data-toggle="modal" data-target="#myOracleModal" value="' + checkwait + '">';
        html += '<span class="glyphicon glyphicon-check" aria-hidden="true"></span></button></td>';
        //html += '<td>' + '<button id=' + id + ' onclick="opt_tomcat(this)" name="start_tomcat" class="btn btn-default" data-toggle="modal" data-target="#myModal">';
        html += '<td>' + '<button id=' + id + ' onclick="opt_oracle(this)" name="start_oracle" class="btn btn-default" data-toggle="modal" data-target="#myOracleModal" value="' + startwait + '">';
        html += '<span class="glyphicon glyphicon-play" aria-hidden="true"></span></button></td>';
        html += '<td>' + '<button id=' + id + ' onclick="opt_oracle(this)" name="stop_oracle" class="btn btn-default" data-toggle="modal" data-target="#myOracleModal" value="' + stopwait + '">';
        html += '<span class="glyphicon glyphicon-stop" aria-hidden="true"></span></button></td>';
    }
    text.append(html);
    $(function () {
        $("[data-toggle='tooltip']").tooltip();
    });
}
//oracle分页--by lvshaohe
function createOraclePage(obj) {
    var page_number = '';
    var to_page = obj.value;
    var current_page = $('#curnpage').text();
    if (to_page == '0') {
        if (current_page == '1') {
            page_number = current_page
        } else {
            page_number = parseInt(current_page) - 1
        }
    } else if (to_page == '9999') {
        page_number = parseInt(current_page) + 1;
    }
    $.ajax({
        type: "GET",
        url: "./../oracleData/",
        datatype: 'json',
        data: {'page': page_number},
        success: function (datas) {
            loadoracledata(datas)
        }
    });
}
//oracle搜索栏
function searchoracle() {
    var search_val = $('#search_oracle').val();
    $.ajax({
        type: "GET",
        url: "/../searchoracle/",
        data: {'data': search_val},
        datatype: "json",
        success: function (datas) {
            loadoracledata(datas);
            $('#preandnext').empty()
        }
    })
}
// 针对oracle数据库服务器的操作--by lvshaohe
function opt_oracle(obj) {
    //进度条当前宽度
    var count = 0;
    var widthcount = 0;
    //定时器变量
    var timer1;
    //获取modal的body
    var oracle_mes = $("#oracle_message");
    //获取button上记录的该操作的超时时间
    var opstime = obj.value;
    //初始化进度条为0
    $('#progstatus').css('width', '0%');
    oracle_mes.empty().append("正在玩命操作，预计" + opstime + "秒内完成！");
    //点击button后，将当前button标记为disabled的状态
    $(obj).addClass('disabled');
    //弹出modal的关闭按钮也变为disabled状态
    $("#messagemodal").prop('disabled', true);
    var id = obj.id;
    var action = obj.name;
    $.ajax({
        type: 'Get',
        url: './../operation/oracle',
        data: {'id': id, 'action': action},
        //ajax调用后触发刷新进度条的任务
        beforSend: showprogress(),
        success: function (data) {
            oracle_mes.empty().append(data['message']);
            //更新状态
            if (data['status'] == '201') {
                $(obj).parent().prevAll('.status').children('span').attr({'class': 'glyphicon glyphicon-ok-sign',});
                $(obj).parent().prevAll('.status').children('span').attr({'title': 'Oracle数据库正常运行'}).tooltip('fixTitle');
            } else if (data['status'] == '202') {
                $(obj).parent().prevAll('.status').children('span').attr({'class': 'glyphicon glyphicon-exclamation-sign'});
                $(obj).parent().prevAll('.status').children('span').attr({'title': 'Oracle数据库状态异常，请联系管理员'}).tooltip('fixTitle');
            } else if (data['status'] == '203') {
                $(obj).parent().prevAll('.status').children('span').attr({'class': 'glyphicon glyphicon-remove-sign'});
                $(obj).parent().prevAll('.status').children('span').attr({'title': 'Oracle数据库已关闭'}).tooltip('fixTitle');
            }
            $(obj).removeClass('disabled');
            $("#messagemodal").removeAttr("disabled");
            //后台调用成功，停止定时器，同时将进度条刷新到100%
            clearInterval(timer1);
            $('#progstatus').css("width", "100%");
        }
    });
    //启动定时器，根据超时时间刷新进度条的状态
    function showprogress() {
        //定义一个定时器，开始刷新进度条
        timer1 = setInterval(function () {
            count = count + 1;
            // alert(count);
            widthcount = (count / opstime) * 100;
            $('#progstatus').css("width", widthcount + "%");
            //如果达到超时时间，停止定时器
            if (parseInt(count) == parseInt(opstime)) {
                clearInterval(timer1);
            }
        }, 1000);
    }
}


//加载mysql数据库相关信息--by lvshaohe
function loadmysqldata(data) {
    //获取数据
    var datas = data['results'];
    var current_page = data['page'];
    var firstrecord = (current_page - 1) * 9 + 1;
    var lastrecord = firstrecord + datas.length - 1;
    var total = Math.ceil(data['total'] / 9);
    //跟新label标签的内容
    $('#curnpage').empty().append(current_page);
    //导入分页栏的数据
    if (current_page == 1) {
        $('.pager .previous').addClass('disabled')
    } else {
        $('.pager .previous').removeClass('disabled')
    }
    if (current_page == total) {
        $('.pager .next').addClass('disabled')
    } else {
        $('.pager .next').removeClass('disabled')
    }
    $('.pager strong:eq(0)').empty().append(current_page);
    $('.pager strong:eq(1)').empty().append(firstrecord);
    $('.pager strong:eq(2)').empty().append(lastrecord);
    $('.pager strong:eq(3)').empty().append(total);
    //导入表格内容
    var text = $('.text');
    text.empty();
    var html = '';
    for (var i = 0; i < datas.length; i++) {
        var id = datas[i]['id'];
        var ip = datas[i]['ipaddress'];
        var host = datas[i]['machine'];
        var dec = datas[i]['description'];
        var status = datas[i]['status'];
        var startwait = datas[i]['startwait'];
        var stopwait = datas[i]['stopwait'];
        var checkwait = datas[i]['checktime'];
        html += '<tr>';
        html += '<td>' + id + '</td>';
        html += '<td class="ipaddress">' + ip + '</td>';
        html += '<td>' + host + '</td>';
        html += '<td>' + dec + '</td>';
        // html += '<td class="status">' + status + '</td>';
        //更新状态
        if (status == '301') {
            html += '<td class="status" ><span class="glyphicon glyphicon-ok-sign" aria-hidden="true" data-toggle="tooltip" title="Mysql正常运行"></span></td>';
        } else if (status == '302' || status == '304' || status == '305') {
            html += '<td class="status" ><span class="glyphicon glyphicon-exclamation-sign" aria-hidden="true" data-toggle="tooltip" title="Mysql状态异常，请联系管理员"></span></td>';
        } else if (status == '303') {
            html += '<td class="status" ><span class="glyphicon glyphicon-remove-sign" aria-hidden="true" data-toggle="tooltip" title="Mysql数据库已关闭"></span></td>';
        }
        html += '<td>' + '<button id=' + id + ' onclick="opt_mysql(this)" name="check_mysql" class="btn btn-default" data-toggle="modal" data-target="#myMysqlModal" value="' + checkwait + '">';
        html += '<span class="glyphicon glyphicon-check" aria-hidden="true"></span></button></td>';
        //html += '<td>' + '<button id=' + id + ' onclick="opt_tomcat(this)" name="start_tomcat" class="btn btn-default" data-toggle="modal" data-target="#myModal">';
        html += '<td>' + '<button id=' + id + ' onclick="opt_mysql(this)" name="start_mysql" class="btn btn-default" data-toggle="modal" data-target="#myMysqlModal" value="' + startwait + '">';
        html += '<span class="glyphicon glyphicon-play" aria-hidden="true"></span></button></td>';
        html += '<td>' + '<button id=' + id + ' onclick="opt_mysql(this)" name="stop_mysql" class="btn btn-default" data-toggle="modal" data-target="#myMysqlModal" value="' + stopwait + '">';
        html += '<span class="glyphicon glyphicon-stop" aria-hidden="true"></span></button></td>';
        html += '</tr>';
    }
    text.append(html);
    //开启tooltip
    $(function () {
        $("[data-toggle='tooltip']").tooltip();
    });
}
//mysql分页--by lvshaohe
function createMsqlPage(obj) {
    var page_number = '';
    var to_page = obj.value;
    var current_page = $('#curnpage').text();
    if (to_page == '0') {
        if (current_page == '1') {
            page_number = current_page
        } else {
            page_number = parseInt(current_page) - 1
        }
    } else if (to_page == '9999') {
        page_number = parseInt(current_page) + 1;
    }
    $.ajax({
        type: "GET",
        url: "./../mysqlData/",
        datatype: 'json',
        data: {'page': page_number},
        success: function (datas) {
            loadmysqldata(datas)
        }
    });
}
//mysql搜索栏
function searchmysql() {
    var search_val = $('#search_mysql').val();
    $.ajax({
        type: "GET",
        url: "/../searchmysql/",
        data: {'data': search_val},
        datatype: "json",
        success: function (datas) {
            loadmysqldata(datas);
            $('#preandnext').empty()
        }
    })
}
// 针对mysql数据库服务器的操作--by lvshaohe
function opt_mysql(obj) {
    //进度条当前宽度
    var count = 0;
    var widthcount = 0;
    //定时器变量
    var timer1;
    //获取modal的body
    var mysql_mes = $("#mysql_message");
    //获取button上记录的该操作的超时时间
    var opstime = obj.value;
    //初始化进度条为0
    $('#progstatus').css('width', '0%');
    mysql_mes.empty().append("正在玩命操作，预计" + opstime + "秒内完成！");
    //点击button后，将当前button标记为disabled的状态
    $(obj).addClass('disabled');
    //弹出modal的关闭按钮也变为disabled状态
    $("#messagemodal").prop('disabled', true);
    var id = obj.id;
    var action = obj.name;
    $.ajax({
        type: 'Get',
        url: './../operation/mysql',
        data: {'id': id, 'action': action},
        //ajax调用后触发刷新进度条的任务
        beforSend: showprogress(),
        success: function (data) {
            mysql_mes.empty().append(data['message']);
            //更新状态
            if (data['status'] == '301') {
                $(obj).parent().prevAll('.status').children('span').attr({'class': 'glyphicon glyphicon-ok-sign'});
                $(obj).parent().prevAll('.status').children('span').attr({'title': 'Mysql正常运行'}).tooltip('fixTitle');
            } else if (data['status'] == '302' || data['status'] == '304' || data['status'] == '305') {
                $(obj).parent().prevAll('.status').children('span').attr({'class': 'glyphicon glyphicon-exclamation-sign'});
                $(obj).parent().prevAll('.status').children('span').attr({'title': 'Mysql异常，请联系管理员'}).tooltip('fixTitle');
            } else if (data['status'] == '303') {
                $(obj).parent().prevAll('.status').children('span').attr({'class': 'glyphicon glyphicon-remove-sign'});
                $(obj).parent().prevAll('.status').children('span').attr({'title': 'Mysql已关闭'}).tooltip('fixTitle');
            }
            $(obj).removeClass('disabled');
            $("#messagemodal").removeAttr("disabled");
            //后台调用成功，停止定时器，同时将进度条刷新到100%
            clearInterval(timer1);
            $('#progstatus').css("width", "100%");
        }
    });
    //启动定时器，根据超时时间刷新进度条的状态
    function showprogress() {
        //定义一个定时器，开始刷新进度条
        timer1 = setInterval(function () {
            count = count + 1;
            //alert(count);
            widthcount = (count / opstime) * 100;
            $('#progstatus').css("width", widthcount + "%");
            //如果达到超时时间，停止定时器
            if (parseInt(count) == parseInt(opstime)) {
                clearInterval(timer1);
            }
        }, 1000);
    }
}


//导入apache数据
function loadapachedata(data) {
    //获取数据
    var datas = data['results'];
    var current_page = data['page'];
    var firstrecord = (current_page - 1) * 9 + 1;
    var lastrecord = firstrecord + datas.length - 1;
    var total = Math.ceil(data['total'] / 9);
    //跟新label标签的内容
    $('#curnpage').empty().append(current_page);
    //导入分页栏的数据
    if (current_page == 1) {
        $('.pager .previous').addClass('disabled')
    } else {
        $('.pager .previous').removeClass('disabled')
    }
    if (current_page == total) {
        $('.pager .next').addClass('disabled')
    } else {
        $('.pager .next').removeClass('disabled')
    }
    $('.pager strong:eq(0)').empty().append(current_page);
    $('.pager strong:eq(1)').empty().append(firstrecord);
    $('.pager strong:eq(2)').empty().append(lastrecord);
    $('.pager strong:eq(3)').empty().append(total);
    var text = $('.text');
    text.empty();
    var html = '';
    for (var i = 0; i < datas.length; i++) {
        var id = datas[i]['id'];
        var ip = datas[i]['ipaddress'];
        var host = datas[i]['machine'];
        var dec = datas[i]['description'];
        var status = datas[i]['status'];
        var startwait = datas[i]['startwait'];
        var stopwait = datas[i]['stopwait'];
        var checkwait = datas[i]['checkwait'];
        html += '<tr>';
        html += '<td>' + id + '</td>';
        html += '<td class="ipaddress">' + ip + '</td>';
        html += '<td>' + host + '</td>';
        html += '<td>' + dec + '</td>';
        //更新状态
        if (status == '401') {
            html += '<td class="status" ><span class="glyphicon glyphicon-ok-sign" aria-hidden="true" data-toggle="tooltip" title="Apache正常运行"></span></td>';
        } else if (status == '402' || status == '404' || status == '405') {
            html += '<td class="status" ><span class="glyphicon glyphicon-exclamation-sign" aria-hidden="true" data-toggle="tooltip" title="Apache异常，请联系管理员"></span></td>';
        } else if (status == '403') {
            html += '<td class="status" ><span class="glyphicon glyphicon-remove-sign" aria-hidden="true" data-toggle="tooltip" title="Apache已关闭"></span></td>';
        }
        html += '<td>' + '<button id=' + id + ' onclick="opt_apache(this)" name="check_apache" class="btn btn-default" data-toggle="modal" data-target="#myApacheModal" value="' + checkwait + '">';
        html += '<span class="glyphicon glyphicon-check" aria-hidden="true"></span></button></td>';
        html += '<td>' + '<button id=' + id + ' onclick="opt_apache(this)" name="start_apache" class="btn btn-default" data-toggle="modal" data-target="#myApacheModal" value="' + startwait + '">';
        html += '<span class="glyphicon glyphicon-play" aria-hidden="true"></span></button></td>';
        html += '<td>' + '<button id=' + id + ' onclick="opt_apache(this)" name="stop_apache" class="btn btn-default" data-toggle="modal" data-target="#myApacheModal" value="' + stopwait + '">';
        html += '<span class="glyphicon glyphicon-stop" aria-hidden="true"></span></button></td>';
        html += '</tr>';
    }
    text.append(html);
    $(function () {
        $("[data-toggle='tooltip']").tooltip();
    });
}
//apache翻页
function createApachePage(obj) {
    var page_number = '';
    var to_page = obj.value;
    var current_page = $('#curnpage').text();
    if (to_page == '0') {
        if (current_page == '1') {
            page_number = current_page
        } else {
            page_number = parseInt(current_page) - 1
        }
    } else if (to_page == '9999') {
        page_number = parseInt(current_page) + 1;
    }
    $.ajax({
        type: "GET",
        url: "./../apacheData/",
        datatype: 'json',
        data: {'page': page_number},
        success: function (datas) {
            loadapachedata(datas)
        }
    });
}
//apache搜索栏
function searchapache() {
    var search_val = $('#search_apache').val();
    $.ajax({
        type: "GET",
        url: "/../searchapache/",
        data: {'data': search_val},
        datatype: "json",
        success: function (datas) {
            loadapachedata(datas);
            $('.preandnext').empty();
        }
    })
}
//apache按钮的操作
function opt_apache(obj) {
    //进度条当前宽度
    var count = 0;
    var widthcount = 0;
    //定时器变量
    var timer1;
    //获取modal的body
    var apache_mes = $("#apache_message");
    //获取button上记录的该操作的超时时间
    var opstime = obj.value;
    //初始化进度条为0
    var myApacheModal = $('#myApacheModal');
    myApacheModal.find('#progstatus').css('width', '0%');
    apache_mes.empty().append("正在玩命操作，预计" + opstime + "秒内完成！");
    //点击button后，将当前button标记为disabled的状态
    $(obj).addClass('disabled');
    //弹出modal的关闭按钮也变为disabled状态
    myApacheModal.find("#messagemodal").prop('disabled', true);
    var id = obj.id;
    var action = obj.name;
    $.ajax({
        type: 'Get',
        url: './../operation/apache',
        data: {'id': id, 'action': action},
        //ajax调用后触发刷新进度条的任务
        beforSend: showprogress(),
        success: function (data) {
            apache_mes.empty().append(data['message']);
            //更新状态
            if (data['status'] == '401') {
                $(obj).parent().prevAll('.status').children('span').attr({'class': 'glyphicon glyphicon-ok-sign'});
                $(obj).parent().prevAll('.status').children('span').attr({'title': 'Apache正常运行'}).tooltip('fixTitle');
            } else if (data['status'] == '402') {
                $(obj).parent().prevAll('.status').children('span').attr({'class': 'glyphicon glyphicon-exclamation-sign'});
                $(obj).parent().prevAll('.status').children('span').attr({'title': 'Apache异常，请联系管理员'}).tooltip('fixTitle');
            } else if (data['status'] == '403') {
                $(obj).parent().prevAll('.status').children('span').attr({'class': 'glyphicon glyphicon-remove-sign'});
                $(obj).parent().prevAll('.status').children('span').attr({'title': 'Apache已关闭'}).tooltip('fixTitle');
            }
            $(obj).removeClass('disabled');
            myApacheModal.find("#messagemodal").removeAttr("disabled");
            //后台调用成功，停止定时器，同时将进度条刷新到100%
            clearInterval(timer1);
            myApacheModal.find('#progstatus').css("width", "100%");
        }
    });
    //启动定时器，根据超时时间刷新进度条的状态
    function showprogress() {
        //定义一个定时器，开始刷新进度条
        timer1 = setInterval(function () {
            count = count + 1;
            //alert(count);
            widthcount = (count / opstime) * 100;
            $('#myApacheModal').find('#progstatus').css("width", widthcount + "%");
            //如果达到超时时间，停止定时器
            if (parseInt(count) == parseInt(opstime)) {
                clearInterval(timer1);
            }
        }, 1000);
    }
}

//导入nginx数据
function loadnginxdata(data) {
    //获取数据
    var datas = data['results'];
    var current_page = data['page'];
    var firstrecord = (current_page - 1) * 9 + 1;
    var lastrecord = firstrecord + datas.length - 1;
    var total = Math.ceil(data['total'] / 9);
    //跟新label标签的内容
    $('#curnpage').empty().append(current_page);
    //导入分页栏的数据
    if (current_page == 1) {
        $('.pager .previous').addClass('disabled');
    } else {
        $('.pager .previous').removeClass('disabled');
    }
    if (current_page == total) {
        $('.pager .next').addClass('disabled')
    } else {
        $('.pager .next').removeClass('disabled')
    }
    $('.pager strong:eq(0)').empty().append(current_page);
    $('.pager strong:eq(1)').empty().append(firstrecord);
    $('.pager strong:eq(2)').empty().append(lastrecord);
    $('.pager strong:eq(3)').empty().append(total);
    var text = $('.text');
    text.empty();
    var html = '';
    for (var i = 0; i < datas.length; i++) {
        var id = datas[i]['id'];
        var ip = datas[i]['ipaddress'];
        var host = datas[i]['machine'];
        var dec = datas[i]['description'];
        var status = datas[i]['status'];
        var startwait = datas[i]['startwait'];
        var stopwait = datas[i]['stopwait'];
        var checkwait = datas[i]['checkwait'];
        html += '<tr>';
        html += '<td>' + id + '</td>';
        html += '<td class="ipaddress">' + ip + '</td>';
        html += '<td>' + host + '</td>';
        html += '<td>' + dec + '</td>';
        //更新状态
        if (status == '501') {
            html += '<td class="status" ><span class="glyphicon glyphicon-ok-sign" aria-hidden="true" data-toggle="tooltip" title="Nginx正常运行"></span></td>';
        } else if (status == '503') {
            html += '<td class="status" ><span class="glyphicon glyphicon-remove-sign" aria-hidden="true" data-toggle="tooltip" title="Nginx已关闭"></span></td>';
        } else {
            html += '<td class="status" ><span class="glyphicon glyphicon-exclamation-sign" aria-hidden="true" data-toggle="tooltip" title="Nginx异常，请联系管理员"></span></td>';
        }
        html += '<td>' + '<button id=' + id + ' onclick="opt_nginx(this)" name="check_nginx" class="btn btn-default" data-toggle="modal" data-target="#myNginxModal" value="' + checkwait + '">';
        html += '<span class="glyphicon glyphicon-check" aria-hidden="true"></span></button></td>';
        html += '<td>' + '<button id=' + id + ' onclick="opt_nginx(this)" name="start_nginx" class="btn btn-default" data-toggle="modal" data-target="#myNginxModal" value="' + startwait + '">';
        html += '<span class="glyphicon glyphicon-play" aria-hidden="true"></span></button></td>';
        html += '<td>' + '<button id=' + id + ' onclick="opt_nginx(this)" name="stop_nginx" class="btn btn-default" data-toggle="modal" data-target="#myNginxModal" value="' + stopwait + '">';
        html += '<span class="glyphicon glyphicon-stop" aria-hidden="true"></span></button></td>';
        html += '</tr>';
    }
    text.append(html);
    $(function () {
        $("[data-toggle='tooltip']").tooltip();
    });
}
//nginx翻页
function createNginxPage(obj) {
    var page_number = '';
    var to_page = obj.value;
    var current_page = $('#curnpage').text();
    if (to_page == '0') {
        if (current_page == '1') {
            page_number = current_page
        } else {
            page_number = parseInt(current_page) - 1
        }
    } else if (to_page == '9999') {
        page_number = parseInt(current_page) + 1;
    }
    $.ajax({
        type: "GET",
        url: "./../nginxData/",
        datatype: 'json',
        data: {'page': page_number},
        success: function (datas) {
            loadnginxdata(datas)
        }
    });
}
//nginx搜索栏
function searchnginx() {
    var search_val = $('#search_nginx').val();
    $.ajax({
        type: "GET",
        url: "/../searchnginx/",
        data: {'data': search_val},
        datatype: "json",
        success: function (datas) {
            loadnginxdata(datas);
            $('.preandnext').empty();
        }
    })
}
//nginx按钮的操作
function opt_nginx(obj) {
    //进度条当前宽度
    var count = 0;
    var widthcount = 0;
    //定时器变量
    var timer1;
    //获取modal的body
    var nginx_mes = $("#nginx_message");
    //获取button上记录的该操作的超时时间
    var opstime = obj.value;
    //初始化进度条为0
    var myNginxModal = $('#myNginxModal');
    myNginxModal.find('#progstatus').css('width', '0%');
    nginx_mes.empty().append("正在玩命操作，预计" + opstime + "秒内完成！");
    //点击button后，将当前button标记为disabled的状态
    $(obj).addClass('disabled');
    //弹出modal的关闭按钮也变为disabled状态
    myNginxModal.find("#messagemodal").prop('disabled', true);
    var id = obj.id;
    var action = obj.name;
    $.ajax({
        type: 'Get',
        url: './../operation/nginx',
        data: {'id': id, 'action': action},
        //ajax调用后触发刷新进度条的任务
        beforSend: showprogress(),
        success: function (data) {
            nginx_mes.empty().append(data['message']);
            //更新状态
            if (data['status'] == '501') {
                $(obj).parent().prevAll('.status').children('span').attr({'class': 'glyphicon glyphicon-ok-sign'});
                $(obj).parent().prevAll('.status').children('span').attr({'title': 'Nginx正常运行'}).tooltip('fixTitle');
            } else if (data['status'] == '502') {
                $(obj).parent().prevAll('.status').children('span').attr({'class': 'glyphicon glyphicon-exclamation-sign'});
                $(obj).parent().prevAll('.status').children('span').attr({'title': 'Nginx异常，请联系管理员'}).tooltip('fixTitle');
            } else if (data['status'] == '503') {
                $(obj).parent().prevAll('.status').children('span').attr({'class': 'glyphicon glyphicon-remove-sign'});
                $(obj).parent().prevAll('.status').children('span').attr({'title': 'Nginx已关闭'}).tooltip('fixTitle');
            }
            $(obj).removeClass('disabled');
            myNginxModal.find("#messagemodal").removeAttr("disabled");
            //后台调用成功，停止定时器，同时将进度条刷新到100%
            clearInterval(timer1);
            myNginxModal.find('#progstatus').css("width", "100%");
        }
    });
    //启动定时器，根据超时时间刷新进度条的状态
    function showprogress() {
        //定义一个定时器，开始刷新进度条
        timer1 = setInterval(function () {
            count = count + 1;
            //alert(count);
            widthcount = (count / opstime) * 100;
            $('#myNginxModal').find('#progstatus').css("width", widthcount + "%");
            //如果达到超时时间，停止定时器
            if (parseInt(count) == parseInt(opstime)) {
                clearInterval(timer1);
            }
        }, 1000);
    }
}


//加载auditlog的内容(报表=>用户操作日志)
$(function () {
    $("ul[id='report'] li").click(function () {
        if (this.id == 'auditlog') {
            $("#workpage").empty().load("/static/maintenance/html/workpage.html #auditlog_workpage");
            $.ajax({
                type: "GET",
                url: "./../auditlogData/",
                datatype: 'json',
                data: {page: 1},
                success: function (datas) {
                    loadauditlogdata(datas)
                }
            });
        }
    })
});
//导入auditlog数据
function loadauditlogdata(datas) {
    var text = $('.text');
    text.empty();
    var html = '';
    for (var i = 0; i < datas.length; i++) {
        var user = datas[i]['oper_user'];
        var host = datas[i]['machine'];
        var ip = datas[i]['IP'];
        var command = datas[i]['command'];
        var message = datas[i]['description'];
        var time = datas[i]['oper_time'];
        html += '<tr>';
        html += '<td>' + user + '</td>';
        html += '<td >' + host + '</td>';
        html += '<td>' + ip + '</td>';
        html += '<td>' + command + '</td>';
        html += '<td>' + message + '</td>';
        html += '<td>' + time + '</td>';
        html += '</tr>';
    }
    text.append(html);
}
// auditlog分页
function page_auditlog(obj) {
    var page_number = $(obj).text();
    $.ajax({
        type: "GET",
        url: "./../auditlogData/",
        datatype: 'json',
        data: {page: page_number},
        success: function (datas) {
            loadauditlogdata(datas)
        }
    });
}


//加载用户信息维护的内容(系统管理=>用户信息维护)
$(function () {
    $("ul[id='systemsetting'] li").click(function () {
        if (this.id == 'usermanagement') {
            $("#workpage").empty().load("/static/maintenance/html/workpage.html #usermanagement_workpage");
            $.ajax({
                type: "GET",
                url: "./../usermanagementData/",
                datatype: 'json',
                data: {page: 1},
                success: function (datas) {
                    loaduserdata(datas)
                }
            });
        }
    })
});
//加载用户数据功能的实现,同时每行数据生成一个修改和删除的按钮：loaduserdata
function loaduserdata(datas) {
    //获取当前用户名称
    var currentuser = $('#welcomeuser').text();
    var group = getcookie('group');
    //alert(document.cookie);
    //alert(group);
    //获取tbody的jquery对象，准备填充从数据库中获取到的数据。填充数据前先将tbody中的内容清空；
    var text = $('.text');
    text.empty();
    var html = '';
    for (var i = 0; i < datas.length; i++) {
        var id = datas[i]['id'];
        var username = datas[i]['username'];
        var password = datas[i]['password'];
        var privilege = datas[i]['privilege'];
        var email = datas[i]['email'];
        var groups = datas[i]['groups'];
        var regtime = datas[i]['regtime'];
        if (currentuser == username || group == 'admin') {
            html += '<tr>';
            html += '<td>' + username + '</td>';
            html += '<td >' + email + '</td>';
            html += '<td>' + privilege + '</td>';
            html += '<td>' + groups + '</td>';
            html += '<td>' + '<button id=' + username + ' onclick="opt_usermanagement_change(this)"  name="change_userinfo" class="btn btn-default" data-toggle="modal" data-target="#userchangemodal">';
            html += '<span class="glyphicon glyphicon glyphicon-pencil" aria-hidden="true"></span> 修改</button>';
            html += '&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;' + '<button id=' + username + ' onclick="opt_usermanagement_delete(this)" name="delete_userinfo" class="btn btn-default"  data-toggle="modal" href="#userdelmodal" >';
            html += '<span class="glyphicon glyphicon glyphicon-remove" aria-hidden="true"></span> 删除</button></td>';
            html += '</tr>';
        }
        else {
            html += '<tr>';
            html += '<td>' + username + '</td>';
            html += '<td >' + email + '</td>';
            html += '<td>' + privilege + '</td>';
            html += '<td>' + groups + '</td>';
            html += '<td>' + '<button id=' + username + ' onclick="opt_usermanagement_change(this)" disabled="disabled" name="change_userinfo" class="btn btn-default" data-toggle="modal" data-target="#userchangemodal">';
            html += '<span class="glyphicon glyphicon glyphicon-pencil" aria-hidden="true"></span> 修改</button>';
            html += '&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;' + '<button id=' + username + ' onclick="opt_usermanagement_delete(this)" disabled="disabled" name="delete_userinfo" class="btn btn-default"  data-toggle="modal" href="#userdelmodal" >';
            html += '<span class="glyphicon glyphicon glyphicon-remove" aria-hidden="true"></span> 删除</button></td>';
            html += '</tr>';
        }
    }
    text.append(html);
    html = '<button id="btadduser" class="btn btn-primary" data-toggle="modal" data-target="#addusermodal"><span class="glyphicon glyphicon-plus"></span> 添加新用户</button>'
    text.append(html);
    if (group != 'admin') {
        $("#btadduser").hide();
    }

}

//获取指定名称的cookie的值
function getcookie(objname) {
    var arrstr = document.cookie.split(";");
    for (var i = 0; i < arrstr.length; i++) {
        var temp = arrstr[i].split("=");
        if (temp[0].trim() == objname)
            return temp[1];
    }
}

// 针对用户信息维护按钮的操作，点击后将部分值记录到modal中：
function opt_usermanagement_delete(obj) {
    var id = obj.id;
    var action = obj.name;
    var del_diag = $("#messageuserdel");
    del_diag.empty().append('<label id="' + id + '"' + 'title="' + action + '">真的要删除用户' + id + "吗?" + '</label>');
}
//用户信息维护：modal中确认删除用户信息，发送数据到后台
function deleteuser(obj) {
    //获取当前弹出窗口中label中记录的用户、操作方法;
    var action = $(obj).parent().siblings().children('label').attr('title');
    var id = $(obj).parent().siblings().children('label').attr('id');
    var del_diag = $("#messageuserdel");
    $.ajax({
        type: 'Get',
        url: './../operation/deleteuser',
        data: {'id': id},
        success: function (data) {
            del_diag.empty().append(data);
            //数据删除后，禁用按钮，同时取消按钮变成退出按钮
            $(obj).prop('disabled', true);
            $('#messagemodal1').text("退出");
            //window.location.reload();
        }
    });
}
//用户信息维护：modal中退出按钮点击时，刷新数据
function refreshdata() {
    //模拟页面点击，刷新页面
    $("#usermanagement").trigger("click");
    //同时将禁用的按钮变成可用状态
    $("#deleteuser").removeAttr("disabled");
    //将退出按钮中的提示修改为取消
    $('#messagemodal1').text("取消");
}


//用户信息维护功能中,点击修改按钮来获取该用户所对应的信息
function opt_usermanagement_change(obj) {
    $('#savemess').attr("disabled", false);
    $('#savemess').text('保存');
    $('#messagemodal2').text('取消');
    var userid = obj.id;
    $.ajax({
        type: "GET",
        url: "./../operation/modifyuserdata/",
        datatype: 'json',
        data: {userid: userid},
        success: function (datas) {
            $("#username").val(datas[1]);  //获取后台传输过来的用户名
            $("#password").val(datas[2]);  //获取后台传输过来的密码
            $("#email").val(datas[3]);     //获取后台传输过来的邮箱
            $("#privilege").val(datas[4]);  //获取后台传输过来的权限
            $("#group").val(datas[5]);     //获取后台传输过来的属组
        }
    })
}

//用户信息修改功能
function opt_save() {
    var username = $('#username').val();
    var password = $('#password').val();
    var email = $('#email').val();
    var privilege = $('#privilege').val();
    var group = $('#group').val();
    $.ajax({
        type: "GET",
        url: "./../operation/saveuserdata/",
        datatype: 'json',
        data: {username: username, password: password, email: email, privilege: privilege, group: group},
        success: function (datas) {
            $('#savemess').attr("disabled", true);
            $("#username").val("");
            $("#password").val("");
            $("#email").val("");
            $("#privilege").val("");
            $("#group").val("");
            $('#savemess').text(datas);
            $('#messagemodal2').text('退出');

        }
    })
}
//用户信息保存成功后，点击退出同时刷新页面数据
function opt_updata() {
    $("#usermanagement").trigger("click");
}


//添加用户
function opt_usermanagement_add() {

    $('#saveuser').attr("disabled", false);
    $('#saveuser').text('确认添加');
    $('#messagemodal3').text('取消');
}
//确认添加
function saveuser() {
    var username = $('#add_username').val();
    var password = $('#add_password').val();
    var email = $('#add_email').val();
    var privilege = $('#add_privilege').val();
    var group = $('#add_group').val();
    $.ajax({
        type: "GET",
        url: "./../operation/adduserdata/",
        datatype: 'json',
        data: {username: username, password: password, email: email, privilege: privilege, group: group},
        success: function (datas) {
            $('#saveuser').attr("disabled", true);
            $("#add_username").val("");
            $("#add_password").val("");
            $("#add_email").val("");
            $("#add_privilege").val("");
            $("#add_group").val("");
            $('#saveuser').text(datas);
            $('#messagemodal3').text('退出');
        }
    })
}

//常用工具功能各页面加载
$(function () {
    $("ul[id='tools'] li").click(function () {
        if (this.id == 'systemhealthcheck') {
            $("#workpage").empty().load("/static/maintenance/html/workpage.html #systemhealthcheck_workpage", function () {
                //$('#machinelist').val('选择应用系统名称');
                //$('#machinelist').selectpicker('render');
                $('#machinelist').hide();
                $('#startchecksystem').attr('disabled', '');
                //$('#maxOption3').show();
                $(".dbservers i[data-priority='1']").addClass('fa fa-database fa-4x');
                $(".dbservers i[data-priority='1']").siblings('h6').text('DB');
                $(".webservers i[data-priority='1']").addClass('fa fa-desktop fa-4x');
                $(".webservers i[data-priority='1']").siblings('h6').text('WEB');
                $(".appservers i[data-priority='1']").addClass('fa fa-server fa-4x');
                $(".appservers i[data-priority='1']").siblings('h6').text('APP');
            });
            //后台获取数据填充systemlist中的内容
            getsystemlist();
        }
    })
});
//ajax方式从后台获取应用系统名称列表，加入到select中进行显示
function getsystemlist() {
    //alert('get data from database');
    $.ajax({
        type: "Get",
        url: "./../operation/getsystemlist/",
        datatype: 'json',
        success: function (data) {
            //$("#systemlist").val(123);
            //$("#systemlist").text(321);
            for (i = 0; i < data.length; i++) {
                $("#systemlist").append('<option>' + data[i]['systemname'] + '</option>');
                //$("#systemlist").append("<option title='"+data[i]['systemname']+"'>" + data[i]['systemname'] + "</option>");
            }
            //alert('ajax succ');
        }
    })
}

//选择应用系统名称后，显示机器清单，同时开始按钮可用
function systemchanged(obj) {
    $("#machinelist").empty();
    //清空其他应用的系统架构图
    $(".dbservers i").removeClass();
    $(".dbservers i").siblings('h6').text('');
    $(".webservers i").removeClass();
    $(".webservers i").siblings('h6').text('');
    $(".appservers i").removeClass();
    $(".appservers i").siblings('h6').text('');
    //如果没有数据，就留一个示例的页面
    $(".dbservers i[data-priority='1']").addClass('fa fa-database fa-4x');
    $(".dbservers i[data-priority='1']").siblings('h6').text('DB');
    $(".webservers i[data-priority='1']").addClass('fa fa-desktop fa-4x');
    $(".webservers i[data-priority='1']").siblings('h6').text('WEB');
    $(".appservers i[data-priority='1']").addClass('fa fa-server fa-4x');
    $(".appservers i[data-priority='1']").siblings('h6').text('APP');
    //alert($("div[id='applayer'] i").css('color'));
    //切换应用系统后将所有的图标变成灰色
    $("div[id='applayer'] i").css({'color': 'lightgrey'});
    $("div[id='weblayer'] i").css({'color': 'lightgrey'});
    $("div[id='dblayer'] i").css({'color': 'lightgrey'});
    //获取某个应用系统对应的服务器清单
    getmachinelist();
    //var sysindx = obj.selectedIndex;
    var systemid = obj.options[obj.selectedIndex].value;
    if (systemid != 0) {
        // $('#machinelist').selectpicker('render');
        // $('#machinelist').show();
        $('#startchecksystem').removeAttr('disabled');

    }
    else {
        // $("#machinelist").empty();
        // $('#machinelist').selectpicker('render');
        // $('#machinelist').show();
        // $('#machinelist').selectpicker('hide');
        // $('#machinelist').selectpicker('render');
        //$('#machinelist').selectpicker('destroy');
        $('#startchecksystem').attr('disabled', '');
    }
}
//从后台数据库中获取当前应用系统对应的服务器清单
function getmachinelist() {
    $("#machinelist").empty();
    var systemname = $("#systemlist option:selected").text();
    //alert(systemname);
    // $("#machinelist").append('<option>'+123+'</option>>');
    $.ajax({
        type: "GET",
        url: "./../operation/getmachinelist/",
        datatype: 'json',
        data: {systemname: systemname},
        success: function (data) {
            window.localStorage.setItem('machines', JSON.stringify(data)); //将获取的数据存到本地
            for (i = 0; i < data.length; i++) {
                $("#machinelist").append('<option title="' + data[i]['types'] + '" value="' + data[i]['levels'] + '">' + data[i]['machinename'] + '</option>');
                //$("#machinelist").append('<option>'+i+'</option>');
                $('#machinelist').selectpicker('render');
                $('#machinelist').selectpicker('refresh');
                $('#machinelist').selectpicker();
                //alert('getdata from database machine list:' + data[i]['machinename']);
                //获取所有的机器清单后，根据获取到的数据生成服务器的架构图
                //生成系统架构图
                var levels = data[i]['levels'];
                var priority = data[i]['priority'];
                var machinename = data[i]['machinename'];
                if (levels == 1) {//DB LAYER层的服务器
                    //显示图标和服务器的名称
                    //alert("hello"); $("ul[id='servicemgr'] li")
                    $(".dbservers i[data-priority='" + priority + "']").addClass('fa fa-database fa-4x');
                    $(".dbservers i[data-priority='" + priority + "']").siblings('h6').text(machinename);
                    //$(".dbservers i[data-priority='" + priority + "']").children('input').removeAttr("hidden");

                }
                if (levels == 2) {//APP LAYER层的服务器
                    //显示图标和服务器的名称
                    //alert("hello"); $("ul[id='servicemgr'] li")
                    $(".appservers i[data-priority='" + priority + "']").addClass('fa fa-server fa-4x');
                    $(".appservers i[data-priority='" + priority + "']").siblings('h6').text(machinename);
                    //$(".appservers i[data-priority='" + priority + "']").children('input').removeAttr("hidden");
                    //css({'visibility':'visible'});visible

                }
                if (levels == 3) {//WEB LAYER层的服务器
                    //显示图标和服务器的名称
                    //alert("hello"); $("ul[id='servicemgr'] li")
                    $(".webservers i[data-priority='" + priority + "']").addClass('fa fa-desktop fa-4x');
                    $(".webservers i[data-priority='" + priority + "']").siblings('h6').text(machinename);
                    //$(".webservers i[data-priority='" + priority + "']").children('input').removeAttr("hidden");

                }
            }
            //初始化任务清单
            initCheckSystemTask(data)
        }
    });
    $('#machinelist').selectpicker('render');
    $('#machinelist').selectpicker('refresh');
    $('#machinelist').selectpicker();
}
//初始化任务清单
function initCheckSystemTask(data) {
    //创建表格
    var myCheckSystem = $('#checkSystemTask');
    var myCheckSystem_table = $('<table class="table"></table>');
    var myCheckSystem_thead = $('<thead><tr><td>系统名称</td><td>机器名称</td><td>运行结果</td></tr></thead>');
    var myCheckSystem_tbody = $('<tbody></tbody>').addClass('progress_tboday');
    //添加数据行
    for (var i = 0; i < data.length; i++) {
        var system_name = data[i]['systemname'];
        var host = data[i]['machinename'];
        var line = '';
        line += '<tr>';
        line += '<td>' + system_name + '</td>';
        line += '<td>' + host + '</td>';
        var progressbar = '';
        progressbar += '<td>';
        progressbar += '<div class="progress">';
        progressbar += '<div class="progress-bar" role="progressbar" aria-valuenow="60" aria-valuemin="0" aria-valuemax="100" style="width: 60%;">';
        progressbar += '<span class="sr-only">60% Complete</span>';
        progressbar += '</div>' + '</div>';
        progressbar += '</td>';
        line += progressbar;
        line += '</tr>';
        myCheckSystem_tbody.append(line)
    }

    myCheckSystem_table.append(myCheckSystem_thead).append(myCheckSystem_tbody);
    myCheckSystem.text('操作结果：').append(myCheckSystem_table)
}
//检查系统操作
function opt_checksystem(obj) {
    //获取本地存储的机器数据
    var mymachines = JSON.parse(window.localStorage.getItem("machines"));
    //alert(mymachines.length);
    $.ajax({
        type: "POST",
        url: "./../operation/checksystem/",
        datatype: 'json',
        data: {
            'machines': mymachines,
            'action': 'checksystem'
        },
        success: function (datas) {
            loadapachedata(datas)
        }
    })

}

//服务器选中后触发修改图中的服务器
function machinechange() {
    var machinelevellist = $("#machinelist").val();//获取选中的对象
    //var machinename = $("#machinelist option:selected").text();//获取选中机器的名称
    //var machinename = $("#machinelist").find("option:selected").text();
    //alert("name="+machinename);
    // for (i=0;i<machinename.length;i++){
    //     alert("name "+i+"="+machinename[i]);
    // }
    //获取多选菜单中服务器的名称，转换成一个字符串数组
    var machinename = $("#machinelist option:selected").map(function () {
        return $(this).val() + ":" + $(this).text();
    }).get().join(",");
    //alert("machinename="+machinename+" type:"+typeof(machinename) );
    var servername = machinename.split(",");
    //针对选中的服务器进行显示
    for (i = 0; i < servername.length; i++) {
        var levels = servername[i].split(":")[0];
        var contents = servername[i].split(":")[1];
        //$("ul[id='servicemgr'] li")
        if (levels == 1) {
            //var obj = $("div[id='dblayer']:contains('"+contents+"')");
            var obj = $("div[id='dblayer'] .dbservers:contains('" + contents + "')");
            obj.children('i').css({'color': 'black'});
            //alert(1)
        }
        if (levels == 2) {
            var obj = $("div[id='applayer'] .appservers:contains('" + contents + "')");
            obj.children('i').css({'color': 'black'});
        }
        if (levels == 3) {
            var obj = $("div[id='weblayer'] .webservers:contains('" + contents + "')");
            obj.children('i').css({'color': 'black'});
        }
    }
    //var unsel = $("#machinelist option:not(:selected)").val();
    //获取多选菜单中所有option对应的value值，不管选中还是没有选中
    var all = $("#machinelist option").map(function () {
        return $(this).val() + ":" + $(this).text();
    }).get().join(",");
    //var sel = $("#machinelist option:selected").val();
    //var len = $("#machinelist").val().length;
    //alert("value="+machinelevellist+" len="+len);
    //alert(machinelevellist);
    var allserver = all.split(',');
    // for(i=0;i<allserver.length;i++){
    //    alert(allserver[i])
    // }
    var currentserver = servername;
    //alert('l='+currentserver.length);
    // for (i = 0; i < currentserver.length; i++) {
    //     alert('xxx=' + currentserver[i])
    // }
    var unselserver = '';
    //allserver是所有服务器清单；currentserver是当前选择的服务器；unselserver是未选择的服务器
    for (var j = 0; j < allserver.length; j++) {
        //alert(allserver[j])
        for (var k = 0; k < currentserver.length; k++) {
            //alert(currentserver[k])
            if (allserver[j] == currentserver[k]) {
                break;
            }
            if (k == currentserver.length - 1) {
                unselserver = unselserver + allserver[j] + ','
            }
        }
    }
    //alert(unselserver);
    //注意一定要在前面赋值，如果在for中直接使用 i < unselserver.split(',').length可能导致结果不正确
    var unselserver = unselserver.split(',');
    // for (i = 0; i < unselserver.length; i++) {
    //     alert(unselserver[i])
    // }
    //alert("all:" + allserver + " cur:" + currentserver + " unsel:" + unselserver);
    //对未选中的服务器将颜色变为灰色
    for (i = 0; i < unselserver.length - 1; i++) {
        var unlevels = unselserver[i].split(":")[0];
        var uncontents = unselserver[i].split(":")[1];
        if (unlevels == 1) {
            var unobj = $("div[id='dblayer'] .dbservers:contains('" + uncontents + "')");
            unobj.children('i').css({'color': 'lightgrey'});
            //alert(1+" "+uncontents)
        }
        if (unlevels == 2) {
            var unobj = $("div[id='applayer'] .appservers:contains('" + uncontents + "')");
            unobj.children('i').css({'color': 'lightgrey'});
            //alert(2+" "+uncontents);
        }
        if (unlevels == 3) {
            var unobj = $("div[id='weblayer'] .webservers:contains('" + uncontents + "')");
            unobj.children('i').css({'color': 'lightgrey'});
            //alert(3+" "+uncontents);
        }
    }
    //alert("len="+len+"lensel="+lensel+"lenunsel="+lenunsel);
    //alert("selected:" + machinelevellist + "all:" + all);
    //遍历当前使用的服务器进行着色:如果当前没有被选择服务器，设置为灰色
    // if (currentserver == '') {
    //     $("div[id='weblayer'] i").css({'color': 'lightgrey'});
    //     $("div[id='applayer'] i").css({'color': 'lightgrey'});
    //     $("div[id='dblayer'] i").css({'color': 'lightgrey'});
    // }
    // else {
    //     for (i = 0; i < currentserver.length; i++) {
    //         //alert(machinelevellist[i]);
    //         if (currentserver[i] == 3) {
    //             $("div[id='weblayer'] i").css({'color': 'black'});
    //             //$("div[id='applayer'] small").text();
    //         }
    //         if (currentserver[i] == 2) {
    //             $("div[id='applayer'] i").css({'color': 'black'});
    //         }
    //         if (currentserver[i] == 1) {
    //             $("div[id='dblayer'] i").css({'color': 'black'});
    //         }
    //     }
    // }

    //遍历服务器，对未使用的服务器进行着色，如果存在未被选择的服务器，将这些服务器设置成灰色
    // if (unselserver == '') {
    //     //$("div[id='applayer'] small").text();
    // }
    // else {
    //     for (i = 0; i < unselserver.length; i++) {
    //         //alert(machinelevellist[i]);
    //         if (unselserver[i] == 3) {
    //             $("div[id='weblayer'] i").css({'color': 'lightgrey'});
    //             //$("div[id='applayer'] small").text();
    //         }
    //         if (unselserver[i] == 2) {
    //             $("div[id='applayer'] i").css({'color': 'lightgrey'});
    //         }
    //         if (unselserver[i] == 1) {
    //             $("div[id='dblayer'] i").css({'color': 'lightgrey'});
    //         }
    //     }
    // }
    //alert("unsel="+unsel);

    //var current_machine=machinename[len-1];
    //alert("len=",len,current_machine);
    //alert($(this).text());
}


//左侧导航栏功能实现：点击一个导航栏后，自动收缩其他已经打开的导航菜单
$(function () {
    $("ul>li>a[data-toggle='collapse']").click(function () {
        //点击一级菜单后隐藏其他一级菜单打开的二级菜单
        $(this).parent().siblings('li').children('a').siblings('ul').collapse('hide');
    })
});

