$(function(){ 
  //监控汇总
  $("#list").jqGrid({
    url:'/zmon/manage?oper=search&from=monitorlist',
    datatype: 'json',
    mtype: 'GET',
    colNames:['监控项ID','监控项名','所属产品线', '日志路径','GREP','GREP-V','监控机器数量','采集项数量','编辑','详细'],
    colModel :[
	  {name:'ID', index:'ID', key:true, width:73}, 
      {name:'NAME', index:'NAME', width:120}, 
      {name:'PRODUCT', index:'PRODUCT', width:120}, 
      {name:'LOGPATH', index:'LOGPATH', editable:true, width:301},
      {name:'GREP', index:'GREP', editable:true, width:120},
	  {name:'GREPV', index:'GREPV', editable:true, width:120},
      {name:'HOSTNUM', index:'HOSTNUM', width:80}, 
      {name:'MONITORNUM', index:'MONITORNUM', width:80},
	  {name: 'myac', width:55, fixed:true, sortable:false, resize:false, formatter:'actions',formatoptions:{keys:true}},
      {name:'editMonitor',index:'editMonitor', width:50,sortable:false},
    ],
    pager: '#pager',
    rowNum:10,
    rowList:[10,30,100],
    sortname: 'id',
	recordpos: 'left',
    sortorder: 'desc',
    viewrecords: true,
	multiselect:false,
	height:262,
	editurl : '/zmon/manage?from=monitor',
    gridComplete: function(){
        var ids = jQuery("#list").jqGrid('getDataIDs');
        for(var i=0;i < ids.length;i++){
            var cl = ids[i];
            alarm = "<input style='height:25px;with:50px' type='button' value='详细' onclick=\"modifyMonitor('"+cl+"');\"  />"; 
            jQuery("#list").jqGrid('setRowData', ids[i], {editMonitor:alarm});
         }   
    },
	onSelectRow: function(ids) {
		if(ids == null) {
			ids=0;
			if(jQuery("#detailhostlist").jqGrid('getGridParam','records') >0 )
			{
				jQuery("#detailhostlist").jqGrid('setGridParam',{url:"/zmon/manage?oper=search&from=hostlist&monitorid="+ids,page:1});
				jQuery("#detailhostlist").jqGrid('setGridParam',{editurl:"/zmon/manage?from=hostlist&monitorid="+ids,page:1});
				jQuery("#detailhostlist").jqGrid('setCaption',"机器列表: "+ids).trigger('reloadGrid');
			}
			if(jQuery("#detailregularlist").jqGrid('getGridParam','records') >0 )
			{
				jQuery("#detailregularlist").jqGrid('setGridParam',{url:"/zmon/manage?oper=search&from=regularlist&monitorid="+ids,page:1});
				jQuery("#detailregularlist").jqGrid('setGridParam',{editurl:"/zmon/manage?from=regularlist&monitorid="+ids,page:1});
				jQuery("#detailregularlist").jqGrid('setCaption',"字段列表: "+ids).trigger('reloadGrid');
			}
		} else {
			jQuery("#detailhostlist").jqGrid('setGridParam',{url:"/zmon/manage?oper=search&from=hostlist&monitorid="+ids,page:1});
			jQuery("#detailhostlist").jqGrid('setGridParam',{editurl:"/zmon/manage?from=hostlist&monitorid="+ids,page:1});
			jQuery("#detailhostlist").jqGrid('setCaption',"机器列表: "+ids).trigger('reloadGrid');		
			jQuery("#detailregularlist").jqGrid('setGridParam',{url:"/zmon/manage?oper=search&from=regularlist&monitorid="+ids,page:1});
			jQuery("#detailregularlist").jqGrid('setGridParam',{editurl:"/zmon/manage?from=regularlist&monitorid="+ids,page:1});
			jQuery("#detailregularlist").jqGrid('setCaption',"字段列表: "+ids).trigger('reloadGrid');
		}
	},
    caption: '监控信息'
  }); 
  //机器详细列表
  jQuery("#detailhostlist").jqGrid({
	height: 200,
   	url:'/zmon/manage?oper=search&from=hostlist',
	datatype: "json",
   	colNames:['机器ID','机器名','IP','编辑'],
   	colModel:[
   		{name:'hostid',index:'hostid', width:80},
   		{name:'hostname',index:'hostname', width:200},
		{name:'hostip',index:'hostip', width:150},
		{name: 'myac', width:80, fixed:true, sortable:false, resize:false, formatter:'actions',formatoptions:{keys:true}},
   	],
   	rowNum:8,
   	rowList:[8,15,30],
   	pager: '#detailhostpager',
   	sortname: 'hostid',
    viewrecords: true,
    sortorder: "asc",
	multiselect: false,
	editurl : '/zmon/manage?from=hostlist&monitorId=' + jQuery("#list").jqGrid('getGridParam','selarrrow'),
	caption:"机器列表",
  });
  //正则详细列表
  jQuery("#detailregularlist").jqGrid({
	height: 200,
   	url:'/zmon/manage?oper=search&from=regularlist',
	datatype: "json",
   	colNames:['字段ID','字段名','正则表达式','编辑'],
   	colModel:[
   		{name:'regularid',index:'regulerid', width:80},
   		{name:'regularname',index:'regularname', width:100},
		{name:'regularex',index:'regularex', editable:true, width:300},
		{name: 'myac', width:80, fixed:true, sortable:false, resize:false, formatter:'actions',formatoptions:{keys:true}},
   	],
   	rowNum:10,
   	rowList:[10,20,30],
   	pager: '#detailregularpager',
   	sortname: 'regularid',
    viewrecords: true,
    sortorder: "asc",
	multiselect: false,
	editurl : '/zmon/manage?from=regularlist',
	caption:"字段列表",
  });
}); 
jQuery("#list").jqGrid('navGrid','#pager',{add:false,edit:false,del:false},
	{}, // edit parameters
	{}, // add parameters
	{reloadAfterSubmit:false} //delete parameters
);

function monflow(monitorID){
    PARAMS = {'monitorID': monitorID}
    get('/zmon/monflow?monitorID=', PARAMS)
}

function modifyMonitor(monitorID){
    var URL = '/zmon/modify';
    var PARAMS = {'monitorId':monitorID};
    get(URL, PARAMS);
    //$('#editMonitorDiv').modal('toggle')
}

function saveChanges(monitorID){
    alert('save changes')
    $('#editMonitorDiv').modal('toggle')
}

function search(){
	var mask = jQuery("#mask").val();
	jQuery("#list").jqGrid('setGridParam',{url:"/zmon/manage?oper=search&from=monitorlist&mask="+mask,page:1}).trigger("reloadGrid");
}

function updateList(){
	data = {};
	data["oper"] = "updatelist";
	product = $("#productline").val();
	if (product == "null"){
		alert("请选择要更新的产品线");
	    return;
	}
	else{
		data["product"] = product;
	}
    $('#updataListBtn').html('菜单更新中...');
    $('#updataListBtn').attr('disabled',true);
    $.ajax({
        url: "/zmon/manage",
        type: 'GET',
        data: data,
        dataType: "json",
        success: function(result){
            if(result.code==200){
                alert("更新成功");
            }
            else{
                alert("更新失败:"+result.txt);
            }
            $('#updataListBtn').html('更新树形菜单');
            $('#updataListBtn').attr('disabled',false);
        },
        error: function(obj, err) {
            alert("更新超时，任务已经转到后台进行处理，请稍候查看！");
            $('#updataListBtn').html('更新树形菜单');
            $('#updataListBtn').attr('disabled',false);
        },
	});
}

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

function reset(){
	jQuery("#mask").val("") 
	jQuery("#list").jqGrid('setGridParam',{url:"/zmon/manage?oper=search&from=monitorlist",page:1}).trigger("reloadGrid");
	jQuery("#detailhostlist").jqGrid('clearGridData','true');
	jQuery("#detailregularlist").jqGrid('clearGridData','true');

}

function deleteMonitor(){
	//var monitorIds = jQuery("#list").jqGrid('getGridParam','selarrrow');
	//var su=jQuery("#list").jqGrid('delRowData','selarrrow');
	//alert(monitorIds);
}

