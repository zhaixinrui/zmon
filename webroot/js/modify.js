//正则表达式模板变量
reTemplate = {}
// 模板索引    button显示的标题     正则的名字     正则表达式           类型-节点    节点的名字     节点的值
// 模板索引    button显示的标题     正则的名字     正则表达式           类型-图表    是否使用均值
reTemplate["0"] = ["lighttpd返回码", "returncode", '.*\".*\" (\\d+) .*', 'node', 'returncode', 'returncode,server_ip']
reTemplate["1"] = ["lighttpd数据量", "dataflow", '.*\".*\" \\d+ (\\d+) .*', 'chart', false]
reTemplate["2"] = ["nginx返回码", "returncode", '.*\".*\" (\\d+) .*', 'node', 'returncode', 'returncode,server_ip']
reTemplate["3"] = ["nginx数据量", "dataflow", '.*\".*\" \\d+ (\\d+) .*', 'chart', false]

function get(URL, PARAMS) {        
$(document).ready(function(){
    var temp = document.createElement("form");        
    temp.action = URL;        
    temp.method = "get";        
    temp.style.display = "none";        
    for (var x in PARAMS) {        
        var opt = document.createElement("textarea");        
        opt.name = x;        
        opt.value = PARAMS[x];        
        // alert(opt.name)        
        temp.appendChild(opt);        
    }        
    document.body.appendChild(temp);        
    temp.submit();        
    return temp;        
})
} 

function changeProduct()
{
	var product = $("#productline").val();
	var url = "js/zmon." + product+ ".js?r="+Math.random()
	//删掉老的js文件
	$("#productline option").each(function(){
		product = $(this).val();
		if ( $("#" + product).length > 0 ) {
			$("#" + product).remove();
		}
	});
	//加载新的js文件
 	var sobj = document.createElement('script'); 
	sobj.type = "text/javascript"; 
	sobj.id = product;
	sobj.src = url; 
	var headobj = document.getElementsByTagName('head')[0]; 
	headobj.appendChild(sobj);	 
}

function getRandomId(){
    var d = new Date()
    return d.getTime();
}

function textChange(ID){
	var $txt = $("#re_name_"+ ID).val();
	var r = getRandomId()
	$("#tr_"+ID).children("td").children(".chartname").attr("value",$txt);
}

function addre(ID){
    var r = getRandomId()
    $(ID).after('<div class="re row-fluid" id="'+ r +'"><div class="input-prepend span3 offset1"><label class="width-auto add-on">字段名</label><input placeholder="自定义字段名,如proctime,reeqip等" onchange="textChange('+ r +')" type="text" id="re_name_'+ r +'" class="re_name"></div><div class="input-prepend span4"><label class="width-auto add-on">正则表达式</label><input placeholder="如需提取用()包裹,否则返回1" type="text" class="re_expr"></div><div class="span2"><button onclick="del('+ r +')" class="btn">删除</button></div></div>');
	var $tr = $('<tr id="tr_'+ r +'" class="chart"><td><input type="button" class="chartname btn" value="NULL" disabled=true ></td><td><input type="checkbox" class="isused" ></td><td><input type="checkbox" class="isaverage"></td></tr>')
	$("#charts").after($tr)
}    

function initTemplate(){
    for (var x in reTemplate){
        txt = reTemplate[x][0];
        $("#re_template").append('<button class="btn" onclick=addretemplate('+ x +')>'+ txt +'</button>');
    }
}

//使用正则模板添加正则
function addretemplate(index){
    var r = getRandomId();
    reName = reTemplate[index][1];
    reExpr = reTemplate[index][2];
    $("#p_re").after('<div id='+ r +' class="re row-fluid"><div class="input-prepend span3 offset1"><label class="width-auto add-on">字段名</label><input class="re_name" id="re_name_'+ r +'" onchange="textChange(' + r +' )" type="text"></div><div class="input-prepend span4"><label class="width-auto add-on">正则表达式</label><input class="re_expr" id="re_expr_'+ r +'" type="text"></div><div class="span2"><button class="btn" onclick=del('+ r +')>删除</button></div></div>');
    $("#re_name_"+r).attr('value',reName);
    $("#re_expr_"+r).attr('value',reExpr);
    var type = reTemplate[index][3];
    //增加节点类型
    if (type == 'node'){
        var $tr = $('<div id=node_'+ r +' class="node row-fluid"><div class="input-prepend span3 offset1"><label class="width-auto add-on">节点名</label><input class="node_name" id="node_name_'+ r +'" type="text"></div><div class="input-prepend span3"><label class="width-auto add-on">包含字段</label><input class="node_child" id="node_expr_'+ r +'" type="text"></div><div class="span2"><button class="btn" onclick=del('+ r +')>删除</button></div></div>');
        $("#p_node").after($tr);
        $("#node_name_"+r).attr('value',reTemplate[index][4]);
        $("#node_expr_"+r).attr('value',reTemplate[index][5]);
    }
    //增加图表类型
    else{   
        var $tr = $('<tr id="tr_'+ r +'" class="chart"><td><input type="button" class="chartname btn" disabled=true value="NULL"></td><td><input type="checkbox" checked=true class="isused"></td><td><input type="checkbox" id="checkbox_'+ r +'" class="isaverage" ></td> </tr>');
        $("#charts").after($tr);
        var isAverage = reTemplate[index][4]
        $("#checkbox_" + r).attr('checked', isAverage)
        textChange(r);
    }
}    

function addnode(p_ID){
    var r = getRandomId()
    $(p_ID).after('<div id='+ r +' class="node row-fluid"><div class="input-prepend span3 offset1"><label class="width-auto add-on">节点名</label><input class="node_name" id="re_name_'+ r +'" type="text" placeholder="自定义节点名"></div><div class="input-prepend span3"><label class="width-auto add-on">包含字段</label><input class="node_child" type="text" placeholder="字段需在第二步中定义，用逗号分隔"></div><div class="span2"><button class="btn" onclick=del('+ r +')>删除</button></div></div>');
}

function del(ID){
    $("#"+ID).html("");
    $("#"+ID).remove();
	$("#tr_"+ID).remove();
	$("#node_"+ID).remove();
}    

function testre(){
    data = {};
    data["log_line"] = $("#log_line").val();
	if (data["log_line"] == ""){
		alert("日志行不能为空");
		return false;
	}
    data["re_expr"] = $("#re_expr").val();
	if (data["re_expr"] == ""){
		alert("正则表达式不能为空");
		return false;
	}
	//提交
    $.ajax({
        url: "/zmon/testre",
        type: 'POST',
        data: data,
        dataType: "json",
        success: function(result){
            if(result.code==200){
                $("#testresult").val(result.msg)
            }
            else{
                alert("测试失败:"+result.msg);
            }
        }
    });
}
function submitModify(monitorId){
	var data = {};
    data["monitorId"] = monitorId;
    data["product"] = $("#productline").val();
	//监控项名设置
    data["monitorname"] = $("#monitorname").val();
	if (data["monitorname"] == ""){
		alert("监控项名不能为空");
		return false;
	}
	//日志路径设置
    data["logpath"] = $("#logpath").val();
	if (data["logpath"] == ""){
		alert("日志路径不能为空");
		return false;
	}
	//机器列表设置
    data["hostName"] = $("#hostName").val();
    data["serviceName"] = $("#serviceName").val();
	if (data["hostName"] == "" && data["serviceName"] == ""){
		alert("机器列表不能为空");
		return false;
	}
	//日志过滤选项
	data["grep"] = $("#grep").val();
    data["grep-v"] = $("#grep-v").val();
	//正则表达式设置
    data["allfield"] = "idc,server_ip,flow";
    $("div.re").each(function(){
       re_name = $(this).children(".input-prepend").children(".re_name").val();
       re_expr = $(this).children(".input-prepend").children(".re_expr").val();
       data["allfield"] += "," + re_name;
	   if (re_name == "" || re_expr == ""){
           alert("字段名或者正则表达式不能为空");
		   return false;
	   }
       data["re_name_" + re_name] = re_expr;
    });
	//图表展示设置
	$("tr.chart").each(function(){
	   var chart_name = $(this).children("td").children(".chartname").val();
       var chart_isused = $(this).children("td").children(".isused").attr('checked');
       //设置为展示图表时检查是否使用均值
	   if (chart_isused!=undefined && chart_isused=="checked"){	
           var chart_isaverage = $(this).children("td").children(".isaverage").attr('checked');
           if (chart_isaverage!=undefined && chart_isaverage=="checked"){
	           data["chart_name_" + chart_name] = true;
           }
           else{
	           data["chart_name_" + chart_name] = false;
           }
	   }
    });
	//树形菜单设置
    $("div.node").each(function(){
       var node_name = $(this).children(".input-prepend").children(".node_name").val();
       var node_child = $(this).children(".input-prepend").children(".node_child").val();
	   if (node_name == "" || node_child == ""){
           alert("节点名或者包含字段不能为空");
		   return false;
	   }	   
	   data["node_name_" + node_name] = node_child;
    });
	//提交
    $.ajax({
        url: "/zmon/modify",
        type: 'POST',
        data: data,
        dataType: "json",
        success: function(result){
            if(result.code==200){
                alert("提交成功!");
            }
            else{
                alert("提交失败:"+result.txt);
            }
        }
    });
}
