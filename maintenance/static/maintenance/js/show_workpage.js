/**
 * Created by d046532 on 2017/7/11.
 */

$(function () {
    $("ul li").click(function () {
        <!-- 导入workPage-->
        if (this.id == 'toms') {
            $("#workpage").empty().load("./../../static/maintenance/html/workpage.html #tom_workpage");
            $.ajax({
                type: "GET",
                url: "./../tomcatData/",
                datatype: 'json',
                success: function (datas) {
                    var text = $('.text');
                    text.empty();
                    var html = '';
                    for (var i = 0; i < datas.length; i++) {
                        var id = datas[i]['id'];
                        var ip = datas[i]['ipaddress'];
                        var host = datas[i]['machine'];
                        var dec = datas[i]['description'];
                        html += '<tr>';
                        html += '<td>' + id + '</td>';
                        html += '<td>' + ip + '</td>';
                        html += '<td>' + host + '</td>';
                        html += '<td>' + dec + '</td>';
                        html += '<td>' + '<button id=' + id + ' onclick="opt_tomcat(this)" name="check_tomcat" class="btn btn-default">';
                        html += '<span class="glyphicon glyphicon-check" aria-hidden="true"></span></button></td>';
                        html += '<td>' + '<button id=' + id + ' onclick="opt_tomcat(this)" name="start_tomcat" class="btn btn-default">';
                        html += '<span class="glyphicon glyphicon-play" aria-hidden="true"></span></button></td>';
                        html += '<td>' + '<button id=' + id + ' onclick="opt_tomcat(this)" name="stop_tomcat" class="btn btn-default">';
                        html += '<span class="glyphicon glyphicon-stop" aria-hidden="true"></span></button></td>';
                        html += '</tr>';
                    }
                    text.append(html);
                },
                error: function (datas) {
                    text.append(datas);
                }
            });
        } else if (this.id == 'oras') {
            $("#workpage").empty().load("./../../static/maintenance/html/workpage.html #ora_workpage");
            $.ajax({
                type: "GET",
                url: "./../oracleData/",
                datatype: 'json',
                success: function (datas) {
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
            })
        }
    });
});


function opt_tomcat(obj) {
    var id = obj.id;
    var action = obj.name;
    $.ajax({
        type: 'Get',
        url: './../operation',
        data: {'id': id, 'action': action},
        success: function (data) {
            $("#tomcat_mes").empty().append(data['message']);
        }
    })
}

