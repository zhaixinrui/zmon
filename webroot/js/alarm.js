$(function(){ 
    //监控策略配置
    $("#threshold_list").jqGrid({
        datatype: 'json',
        mtype: 'GET',
        colNames:['ID', '监控key','上限阈值', '下限阈值','上涨变化率阈值','下降变化率阈值','屏蔽时间','编辑'],
        colModel :[
          {name:'id', index:'id', key:true, width:50}, 
    	  {name:'key', width:210, editable:true,editoptions:{size:10}}, 
          {name:'qps_upper', width:60, editable:true,editoptions:{size:10}}, 
          {name:'qps_floor', index:'floor', width:60, editable:true,editoptions:{size:10}}, 
          {name:'change_rate_up', index:'change_rate', width:100, editable:true,editoptions:{size:10}}, 
          {name:'change_rate_down', index:'change_rate', width:100, editable:true,editoptions:{size:10}}, 
          {name:'shield_time', index:'shield_time', width:100, editable:true,editoptions:{size:10}}, 
    	  {name: 'myac', width:75, fixed:true, sortable:false, resize:false, formatter:'actions',formatoptions:{keys:true}},
        ],
        pager: '#threshold_pager',
        rowNum:100,
        rowList:[10,30,100],
        sortname: 'id',
    	recordpos: 'left',
        sortorder: 'desc',
        viewrecords: true,
    	multiselect:false,
    	height:300,
        caption: '监控策略配置',
    }); 
    $("#threshold_list").jqGrid('inlineNav',"#threshold_pager");

    //白名单配置
    $("#whitelist_list").jqGrid({
        datatype: 'json',
        mtype: 'GET',
        colNames:['ID','监控key','编辑'],
        colModel :[
          {name:'id', index:'id', key:true, width:50}, 
    	  {name:'key', index:'key', width:530, editable:true,editoptions:{size:10}}, 
    	  {name: 'myac', width:200, fixed:true, sortable:false, resize:false, formatter:'actions',formatoptions:{keys:true}},
        ],
        pager: '#whitelist_pager',
        rowNum:100,
        rowList:[10,30,100],
        sortname: 'id',
    	recordpos: 'left',
        sortorder: 'desc',
        viewrecords: true,
    	multiselect:false,
    	height:200,
        caption: '白名单配置',
    }); 
  
    //报警接收人配置
    $("#receiver_list").jqGrid({
        datatype: 'json',
        mtype: 'GET',
        colNames:['ID','监控key','短信接收人', '邮件接收人','编辑'],
        colModel :[
          {name:'id', index:'id', key:true, width:50}, 
    	  {name:'key', width:220, editable:true,editoptions:{size:10}}, 
          {name:'mobile', width:200, editable:true,editoptions:{size:10}}, 
          {name:'mail', width:200, editable:true,editoptions:{size:10}}, 
    	  {name: 'myac', width:100, fixed:true, sortable:false, resize:false, formatter:'actions',formatoptions:{keys:true}},
        ],
        pager: '#receiver_pager',
        rowNum:100,
        rowList:[10,30,100],
        sortname: 'id',
    	recordpos: 'left',
        sortorder: 'desc',
        viewrecords: true,
    	multiselect:false,
    	height:200,
        caption: '报警接收人配置',
    }); 

    //更换产品线
    $(".a_product").click(function(){ 
        var rootUrl = "/zmon/alarm"
        var product = $(this).text(); 
        var ids = new Array("threshold_list", "receiver_list", "whitelist_list");
        $(ids).each(function(){
            $("#"+this).jqGrid('setGridParam',{url:"/zmon/alarm?oper=search&from="+this+"&product="+product})
            $("#"+this).jqGrid('setGridParam',{editurl:"/zmon/alarm?from="+this+"&product="+product});
            $("#"+this).jqGrid('setCaption','产品线 : ' + product).trigger('reloadGrid'); 
        });
    });

    //新增阈值配置
    $("#add_threshold").click(function(){ 
        jQuery("#threshold_list").jqGrid('editGridRow',"new",{height:350,width:400,reloadAfterSubmit:false}); 
    });

    //新增接收人配置
    $("#add_receiver").click(function(){ 
        jQuery("#receiver_list").jqGrid('editGridRow',"new",{height:280,width:400,reloadAfterSubmit:false}); 
    });

    //新增白名单配置
    $("#add_whitelist").click(function(){ 
        jQuery("#whitelist_list").jqGrid('editGridRow',"new",{height:280,width:400,reloadAfterSubmit:false}); 
    });

}); 

