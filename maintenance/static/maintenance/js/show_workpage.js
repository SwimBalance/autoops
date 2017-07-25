/**
 * Created by d046532 on 2017/7/11.
 */

$(function () {
    $("ul[id='servicemgr'] li").click(function () {
        <!-- 导入workPage-->
        if (this.id == 'toms') {
            $("#workpage").empty().load("/static/maintenance/html/workpage.html #tom_workpage");
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
            $.ajax({
                type: "GET",
                url: "./../oracleData/",
                datatype: 'json',
                success: function (datas) {
                    loadoracledata(datas)
                }
            })
        }
    });
});

// 针对tomcat服务器的操作
function opt_tomcat(obj) {
    var tomcat_mes = $("#message");
    //获取button上记录的该操作的超时时间
    var opstime=obj.value;
    //alert(opstime);
    $('#progstatus').css('width','0%');
    tomcat_mes.empty().append("正在玩命操作，预计"+opstime+"秒内完成！");
    //点击button后，将当前button标记为disabled的状态
    $(obj).addClass('disabled');
    //弹出modal的关闭按钮也变为disabled状态
    $("#messagemodal").prop('disabled',true);
    var id = obj.id;
    var action = obj.name;
    $.ajax({
        type: 'Get',
        url: './../operation',
        data: {'id': id, 'action': action},
        success: function (data) {
            tomcat_mes.empty().append(data['message']);
            $('#progstatus').css('width','100%');
            //更新状态
            if (data['status'] == '101') {
                $(obj).parent().prevAll('.status').children('span').attr('class', 'glyphicon glyphicon-ok-sign')
            } else if (data['status'] == '102' || data['status'] == '104' || data['status'] == '105') {
                $(obj).parent().prevAll('.status').children('span').attr('class', 'glyphicon glyphicon-exclamation-sign')
            } else if (data['status'] == '103') {
                $(obj).parent().prevAll('.status').children('span').attr('class', 'glyphicon glyphicon-remove-sign')
            }
            $(obj).removeClass('disabled');
            $("#messagemodal").removeAttr("disabled");
        }
    });
}
// 分页
function page(obj) {
    var page_number = $(obj).text();
    $.ajax({
        type: "GET",
        url: "./../tomcatData/",
        datatype: 'json',
        data: {page: page_number},
        success: function (datas) {
            loadtomcatdata(datas)
        }
    });
}
//导入tomcat数据
function loadtomcatdata(datas) {
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
            html += '<td class="status" ><span class="glyphicon glyphicon-exclamation-sign" aria-hidden="true"  data-toggle="tooltip" title="Tomcat异常，请联系管理员"></span></td>';
        } else if (status == '103') {
            html += '<td class="status" ><span class="glyphicon glyphicon-remove-sign" aria-hidden="true" data-toggle="tooltip" title="Tomcat已关闭"></span></td>';
        }
        html += '<td>' + '<button id=' + id + ' onclick="opt_tomcat(this)" name="check_tomcat" class="btn btn-default" data-toggle="modal" data-target="#myModal">';
        html += '<span class="glyphicon glyphicon-check" aria-hidden="true"></span></button></td>';
        //html += '<td>' + '<button id=' + id + ' onclick="opt_tomcat(this)" name="start_tomcat" class="btn btn-default" data-toggle="modal" data-target="#myModal">';
        html += '<td>' + '<button id=' + id + ' onclick="opt_tomcat(this)" name="start_tomcat" class="btn btn-default" data-toggle="modal" data-target="#myModal" value="'+startwait+'">';
        html += '<span class="glyphicon glyphicon-play" aria-hidden="true"></span></button></td>';
        html += '<td>' + '<button id=' + id + ' onclick="opt_tomcat(this)" name="stop_tomcat" class="btn btn-default" data-toggle="modal" data-target="#myModal" value="'+stopwait+'">';
        html += '<span class="glyphicon glyphicon-stop" aria-hidden="true"></span></button></td>';
        // += '<td class="startwait" style="display:none" >' + startwait + '</td>';
        //html += '<td class="stopwait"  style="display:none">' + stopwait + '</td>';
        html += '</tr>';
    }
    text.append(html);
    $(function () { $("[data-toggle='tooltip']").tooltip(); });
}
//搜索栏
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
function loadoracledata(datas) {
    var html = '';
    for (var i = 0; i < datas.length; i++) {
        var id = datas[i]['message'];
        var ip = datas[i]['message'];
        var host = datas[i]['message'];
        var dec = datas[i]['message'];
        html += '<tr>';
        html += '<td>' + id + '</td>';
        html += '<td>' + ip + '</td>';
        html += '<td>' + host + '</td>';
        html += '<td>' + dec + '</td>';
        html += '<td>' + '<button id=' + id + ' onclick="opt_tomcat(this)" name="check_tomcat" class="btn btn-default">';
        html += '<span class="glyphicon glyphicon-align-left" aria-hidden="true">' + '</span>';
        html += '</button>' + '</td>';
        html += '<td>' + '<button id=' + id + ' onclick="opt_tomcat(this)" name="start_tomcat">start</button>' + '</td>';
        html += '<td>' + '<button id=' + id + ' onclick="opt_tomcat(this)" name="stop_tomcat">stop</button>' + '</td>';
        html += '</tr>';
    }
    var text = $('.text');
    text.empty().append(html);
}

