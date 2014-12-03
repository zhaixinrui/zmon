$(function() {
    Zmon.init();
});

var Zmon = {
    init: function() {
        this.initZtree();
        this.initTimeSelect();
        this.initHighcharts();
    },
    initZtree: function() {
        $.ajaxSetup({
            'beforeSend': function(xhr) {
                if (xhr.overrideMimeType)
                    xhr.overrideMimeType('text/plain');
            }
        });
        this.ztree = $('#treeview').zTree({
            root: {                
                nodes: [{
                    name: 'monflow',
                    open: true,
                    nodes: [ 
{
name: 'qing',
open: false,
nodes: [
{
name: 'front',
isKey: true,
valueNames: [
{
name: 'proctime',
unit: 'None',
hidden: true
},
{
name: 'proctime_average',
unit: 'None',
divide: true,
dividend: 'proctime',
divisor: 'flow'
},
{
name: 'flow',
unit: 'None'
},
],
nodes: [
{
name: 'returncode',
isListKey: true,
isParent: true,
},
{
name: 'server',
isListKey: true,
isParent: true,
},
]
},
{
name: 'spusvr',
isKey: true,
valueNames: [
{
name: 'proctime',
unit: 'None',
hidden: true
},
{
name: 'proctime_average',
unit: 'None',
divide: true,
dividend: 'proctime',
divisor: 'flow'
},
{
name: 'flow',
unit: 'None'
},
],
nodes: [
{
name: 'spusvr_product',
isListKey: true,
isParent: true,
},
{
name: 'spusvr_server',
isListKey: true,
isParent: true,
},
]
},
]
},
{
name: 'pic',
open: false,
nodes: [
{
name: 'zip',
isKey: true,
valueNames: [
{
name: 'dateflow',
unit: 'None',
hidden: true
},
{
name: 'dateflow_average',
unit: 'None',
divide: true,
dividend: 'dateflow',
divisor: 'flow'
},
{
name: 'flow',
unit: 'None'
},
],
nodes: [
{
name: 'url',
isListKey: true,
isParent: true,
},
{
name: 'server',
isListKey: true,
isParent: true,
},
]
},
{
name: 'upload',
isKey: true,
valueNames: [
{
name: 'flow',
unit: 'None'
},
],
nodes: [
{
name: 'url',
isListKey: true,
isParent: true,
},
{
name: 'server',
isListKey: true,
isParent: true,
},
]
},
{
name: 'favo',
isKey: true,
valueNames: [
{
name: 'flow',
unit: 'None'
},
],
nodes: [
{
name: 'server',
isListKey: true,
isParent: true,
},
]
},
{
name: 'view',
isKey: true,
valueNames: [
{
name: 'proctime',
unit: 'None',
hidden: true
},
{
name: 'proctime_average',
unit: 'None',
divide: true,
dividend: 'proctime',
divisor: 'flow'
},
{
name: 'flow',
unit: 'None'
},
],
nodes: [
{
name: 'url',
isListKey: true,
isParent: true,
},
{
name: 'server',
isListKey: true,
isParent: true,
},
]
},
]
},
{
name: 'passport',
open: false,
nodes: [
{
name: 'dbgateadapter',
isKey: true,
valueNames: [
{
name: 'proctime',
unit: 'None',
hidden: true
},
{
name: 'proctime_average',
unit: 'None',
divide: true,
dividend: 'proctime',
divisor: 'flow'
},
{
name: 'flow',
unit: 'None'
},
],
nodes: [
{
name: 'reqip',
isListKey: true,
isParent: true,
},
{
name: 'server',
isListKey: true,
isParent: true,
},
]
},
{
name: 'passgate',
isKey: true,
valueNames: [
{
name: 'proctime',
unit: 'None',
hidden: true
},
{
name: 'proctime_average',
unit: 'None',
divide: true,
dividend: 'proctime',
divisor: 'flow'
},
{
name: 'flow',
unit: 'None'
},
],
nodes: [
{
name: 'app',
isListKey: true,
isParent: true,
},
{
name: 'down_service',
isListKey: true,
isParent: true,
},
{
name: 'server',
isListKey: true,
isParent: true,
},
]
},
{
name: 'kdss',
isKey: true,
valueNames: [
{
name: 'proctime',
unit: 'None',
hidden: true
},
{
name: 'proctime_average',
unit: 'None',
divide: true,
dividend: 'proctime',
divisor: 'flow'
},
{
name: 'flow',
unit: 'None'
},
],
nodes: [
{
name: 'cmdno',
isListKey: true,
isParent: true,
},
{
name: 'app',
isListKey: true,
isParent: true,
},
{
name: 'server',
isListKey: true,
isParent: true,
},
]
},
{
name: 'ssnexpire',
isKey: true,
valueNames: [
{
name: 'expire_kick',
unit: 'None'
},
{
name: 'topk_kick',
unit: 'None'
},
{
name: 'flow',
unit: 'None'
},
{
name: 'proc_time',
unit: 'None',
hidden: true
},
{
name: 'proc_time_average',
unit: 'None',
divide: true,
dividend: 'proc_time',
divisor: 'flow'
},
],
nodes: [
{
name: 'expire_kick',
isListKey: true,
isParent: true,
},
{
name: 'topk_kick',
isListKey: true,
isParent: true,
},
{
name: 'remstat',
isListKey: true,
isParent: true,
},
{
name: 'ret',
isListKey: true,
isParent: true,
},
{
name: 'server',
isListKey: true,
isParent: true,
},
]
},
{
name: 'ssngate',
isKey: true,
valueNames: [
{
name: 'proctime',
unit: 'None',
hidden: true
},
{
name: 'proctime_average',
unit: 'None',
divide: true,
dividend: 'proctime',
divisor: 'flow'
},
{
name: 'flow',
unit: 'None'
},
],
nodes: [
{
name: 'cmdno',
isListKey: true,
isParent: true,
},
{
name: 'app',
isListKey: true,
isParent: true,
},
{
name: 'server',
isListKey: true,
isParent: true,
},
]
},
{
name: 'ssncm_ic',
isKey: true,
valueNames: [
{
name: 'proctime',
unit: 'None'
},
{
name: 'flow',
unit: 'None'
},
],
nodes: [
{
name: 'cmdno',
isListKey: true,
isParent: true,
},
{
name: 'server',
isListKey: true,
isParent: true,
},
]
},
{
name: 'passcache',
isKey: true,
valueNames: [
{
name: 'process_time_us',
unit: 'None',
hidden: true
},
{
name: 'process_time_us_average',
unit: 'None',
divide: true,
dividend: 'process_time_us',
divisor: 'flow'
},
{
name: 'proctime',
unit: 'None',
hidden: true
},
{
name: 'proctime_average',
unit: 'None',
divide: true,
dividend: 'proctime',
divisor: 'flow'
},
{
name: 'flow',
unit: 'None'
},
{
name: 'reqnum',
unit: 'None',
hidden: true
},
{
name: 'reqnum_average',
unit: 'None',
divide: true,
dividend: 'reqnum',
divisor: 'flow'
},
],
nodes: [
{
name: 'cmdno',
isListKey: true,
isParent: true,
},
{
name: 'errno',
isListKey: true,
isParent: true,
},
{
name: 'server',
isListKey: true,
isParent: true,
},
{
name: 'err_code',
isListKey: true,
isParent: true,
},
]
},
{
name: 'reg',
isKey: true,
valueNames: [
{
name: 'PROCTIME',
unit: 'None',
hidden: true
},
{
name: 'PROCTIME_average',
unit: 'None',
divide: true,
dividend: 'PROCTIME',
divisor: 'flow'
},
{
name: 'flow',
unit: 'None'
},
],
nodes: [
{
name: 'error_no',
isListKey: true,
isParent: true,
},
{
name: 'post',
isListKey: true,
isParent: true,
},
{
name: 'reg',
isListKey: true,
isParent: true,
},
{
name: 'server',
isListKey: true,
isParent: true,
},
]
},
{
name: 'accsug',
isKey: true,
valueNames: [
{
name: 'process_time',
unit: 'None',
hidden: true
},
{
name: 'process_time_average',
unit: 'None',
divide: true,
dividend: 'process_time',
divisor: 'flow'
},
{
name: 'flow',
unit: 'None'
},
],
nodes: [
{
name: 'cmdno',
isListKey: true,
isParent: true,
},
{
name: 'svrname',
isListKey: true,
isParent: true,
},
{
name: 'server',
isListKey: true,
isParent: true,
},
]
},
{
name: 'dbgate',
isKey: true,
valueNames: [
{
name: 'proctime',
unit: 'None',
hidden: true
},
{
name: 'proctime_average',
unit: 'None',
divide: true,
dividend: 'proctime',
divisor: 'flow'
},
{
name: 'field_num',
unit: 'None',
hidden: true
},
{
name: 'field_num_average',
unit: 'None',
divide: true,
dividend: 'field_num',
divisor: 'flow'
},
{
name: 'flow',
unit: 'None'
},
{
name: 'query_num',
unit: 'None',
hidden: true
},
{
name: 'query_num_average',
unit: 'None',
divide: true,
dividend: 'query_num',
divisor: 'flow'
},
{
name: 'cacheget',
unit: 'None',
hidden: true
},
{
name: 'cacheget_average',
unit: 'None',
divide: true,
dividend: 'cacheget',
divisor: 'flow'
},
{
name: 'db_query',
unit: 'None',
hidden: true
},
{
name: 'db_query_average',
unit: 'None',
divide: true,
dividend: 'db_query',
divisor: 'flow'
},
],
nodes: [
{
name: 'cmdno',
isListKey: true,
isParent: true,
},
{
name: 'mdbstrict',
isListKey: true,
isParent: true,
},
{
name: 'server',
isListKey: true,
isParent: true,
},
]
},
{
name: 'dbcm',
isKey: true,
valueNames: [
{
name: 'proctime',
unit: 'None',
hidden: true
},
{
name: 'proctime_average',
unit: 'None',
divide: true,
dividend: 'proctime',
divisor: 'flow'
},
{
name: 'flow',
unit: 'None'
},
],
nodes: [
{
name: 'cmdno',
isListKey: true,
isParent: true,
},
{
name: 'server',
isListKey: true,
isParent: true,
},
]
},
{
name: 'pdcui',
isKey: true,
valueNames: [
{
name: 'proctime',
unit: 'None',
hidden: true
},
{
name: 'proctime_average',
unit: 'None',
divide: true,
dividend: 'proctime',
divisor: 'flow'
},
{
name: 'flow',
unit: 'None'
},
],
nodes: [
{
name: 'cmdno',
isListKey: true,
isParent: true,
},
{
name: 'server',
isListKey: true,
isParent: true,
},
]
},
{
name: 'pusrinfo',
isKey: true,
valueNames: [
{
name: 'proctime',
unit: 'None',
hidden: true
},
{
name: 'proctime_average',
unit: 'None',
divide: true,
dividend: 'proctime',
divisor: 'flow'
},
{
name: 'flow',
unit: 'None'
},
],
nodes: [
{
name: 'app',
isListKey: true,
isParent: true,
},
{
name: 'server',
isListKey: true,
isParent: true,
},
]
},
{
name: 'batchuserinfo',
isKey: true,
valueNames: [
{
name: 'proctime',
unit: 'None',
hidden: true
},
{
name: 'proctime_average',
unit: 'None',
divide: true,
dividend: 'proctime',
divisor: 'flow'
},
{
name: 'flow',
unit: 'None'
},
],
nodes: [
{
name: 'cmdno',
isListKey: true,
isParent: true,
},
{
name: 'server',
isListKey: true,
isParent: true,
},
]
},
{
name: 'login',
isKey: true,
valueNames: [
{
name: 'PROCTIME',
unit: 'None',
hidden: true
},
{
name: 'PROCTIME_average',
unit: 'None',
divide: true,
dividend: 'PROCTIME',
divisor: 'flow'
},
{
name: 'flow',
unit: 'None'
},
],
nodes: [
{
name: 'error_no',
isListKey: true,
isParent: true,
},
{
name: 'post',
isListKey: true,
isParent: true,
},
{
name: 'login',
isListKey: true,
isParent: true,
},
{
name: 'server',
isListKey: true,
isParent: true,
},
]
},
{
name: 'ssnlogic',
isKey: true,
valueNames: [
{
name: 'proctime',
unit: 'None',
hidden: true
},
{
name: 'proctime_average',
unit: 'None',
divide: true,
dividend: 'proctime',
divisor: 'flow'
},
{
name: 'flow',
unit: 'None'
},
],
nodes: [
{
name: 'device',
isListKey: true,
isParent: true,
},
{
name: 'cmdno',
isListKey: true,
isParent: true,
},
{
name: 'app',
isListKey: true,
isParent: true,
},
{
name: 'syn',
isListKey: true,
isParent: true,
},
{
name: 'server',
isListKey: true,
isParent: true,
},
]
},
]
},
{
name: 'orp',
open: false,
nodes: [
{
name: 'router',
isKey: true,
valueNames: [
{
name: 'dataflow',
unit: 'None',
hidden: true
},
{
name: 'dataflow_average',
unit: 'None',
divide: true,
dividend: 'dataflow',
divisor: 'flow'
},
{
name: 'flow',
unit: 'None'
},
{
name: 'proc_time',
unit: 'None',
hidden: true
},
{
name: 'proc_time_average',
unit: 'None',
divide: true,
dividend: 'proc_time',
divisor: 'flow'
},
],
nodes: [
{
name: 'router_product',
isListKey: true,
isParent: true,
},
{
name: 'router_server',
isListKey: true,
isParent: true,
},
]
},
{
name: 'inrouter',
isKey: true,
valueNames: [
{
name: 'dataflow',
unit: 'None'
},
{
name: 'flow',
unit: 'None'
},
{
name: 'proc_time',
unit: 'None',
hidden: true
},
{
name: 'proc_time_average',
unit: 'None',
divide: true,
dividend: 'proc_time',
divisor: 'flow'
},
],
nodes: [
{
name: 'inrouter_product',
isListKey: true,
isParent: true,
},
{
name: 'inrouter_server',
isListKey: true,
isParent: true,
},
]
},
]
},
{
name: 'space',
open: false,
nodes: [
{
name: 'msgui',
isKey: true,
valueNames: [
{
name: 'proctime',
unit: 'None',
hidden: true
},
{
name: 'proctime_average',
unit: 'None',
divide: true,
dividend: 'proctime',
divisor: 'flow'
},
{
name: 'flow',
unit: 'None'
},
],
nodes: [
{
name: 'msgui_product',
isListKey: true,
isParent: true,
},
{
name: 'msgui_server',
isListKey: true,
isParent: true,
},
]
},
{
name: 'imgbaseprocserver',
isKey: true,
valueNames: [
{
name: 'proctime',
unit: 'None',
hidden: true
},
{
name: 'proctime_average',
unit: 'None',
divide: true,
dividend: 'proctime',
divisor: 'flow'
},
{
name: 'flow',
unit: 'None'
},
],
nodes: [
{
name: 'server',
isListKey: true,
isParent: true,
},
]
},
{
name: 'imgcache',
isKey: true,
valueNames: [
{
name: 'imgmeta_proctime',
unit: 'None',
hidden: true
},
{
name: 'imgmeta_proctime_average',
unit: 'None',
divide: true,
dividend: 'imgmeta_proctime',
divisor: 'flow'
},
{
name: 'proctime',
unit: 'None',
hidden: true
},
{
name: 'proctime_average',
unit: 'None',
divide: true,
dividend: 'proctime',
divisor: 'flow'
},
{
name: 'hit',
unit: 'None',
hidden: true
},
{
name: 'hit_average',
unit: 'None',
divide: true,
dividend: 'hit',
divisor: 'flow'
},
{
name: 'flow',
unit: 'None'
},
{
name: 'imgbase_proctime',
unit: 'None',
hidden: true
},
{
name: 'imgbase_proctime_average',
unit: 'None',
divide: true,
dividend: 'imgbase_proctime',
divisor: 'flow'
},
{
name: 'imgdata_proctime',
unit: 'None',
hidden: true
},
{
name: 'imgdata_proctime_average',
unit: 'None',
divide: true,
dividend: 'imgdata_proctime',
divisor: 'flow'
},
],
nodes: [
{
name: 'imgcahce_server',
isListKey: true,
isParent: true,
},
{
name: 'imgcahce_product',
isListKey: true,
isParent: true,
},
]
},
{
name: 'imgcm',
isKey: true,
valueNames: [
{
name: 'proctime',
unit: 'None',
hidden: true
},
{
name: 'proctime_average',
unit: 'None',
divide: true,
dividend: 'proctime',
divisor: 'flow'
},
{
name: 'flow',
unit: 'None'
},
],
nodes: [
{
name: 'product',
isListKey: true,
isParent: true,
},
{
name: 'server',
isListKey: true,
isParent: true,
},
]
},
{
name: 'feeui',
isKey: true,
valueNames: [
{
name: 'proctime',
unit: 'None',
hidden: true
},
{
name: 'proctime_average',
unit: 'None',
divide: true,
dividend: 'proctime',
divisor: 'flow'
},
{
name: 'flow',
unit: 'None'
},
],
nodes: [
{
name: 'feedui_product',
isListKey: true,
isParent: true,
},
{
name: 'feedui_server',
isListKey: true,
isParent: true,
},
]
},
{
name: 'imgdata',
isKey: true,
valueNames: [
{
name: 'data_len',
unit: 'None'
},
{
name: 'proctime',
unit: 'None',
hidden: true
},
{
name: 'proctime_average',
unit: 'None',
divide: true,
dividend: 'proctime',
divisor: 'flow'
},
{
name: 'flow',
unit: 'None'
},
],
nodes: [
{
name: 'cmdno',
isListKey: true,
isParent: true,
},
{
name: 'svrname',
isListKey: true,
isParent: true,
},
{
name: 'server',
isListKey: true,
isParent: true,
},
]
},
{
name: 'imgrelay',
isKey: true,
valueNames: [
{
name: 'proctime',
unit: 'None',
hidden: true
},
{
name: 'proctime_average',
unit: 'None',
divide: true,
dividend: 'proctime',
divisor: 'flow'
},
{
name: 'flow',
unit: 'None'
},
],
nodes: [
{
name: 'cmdno',
isListKey: true,
isParent: true,
},
{
name: 'svrname',
isListKey: true,
isParent: true,
},
{
name: 'server',
isListKey: true,
isParent: true,
},
]
},
]
},
	
                    ] // end of monflow nodes
                }] // end of root nodes
            },
            async: true,
            asyncUrl: function(node) {
                var list_key = Zmon.getNodeListKey(node);
                var where = Zmon.getNodeWhere(node);
                return 'zlist?' + $.param({list_key: list_key, where: where});
            },
            expandSpeed: '',
            showIcon: false,
            checkable: true,
            checkType: {'Y': '', 'N': ''},
            callback: {
                click: function(event, treeId, treeNode) {
                    Zmon.ztree.uncheckAllNodes();
                    treeNode.checked = true;
                    Zmon.ztree.updateNode(treeNode);

                    $('#update').click();
                },
                beforeChange: function(treeId, treeNode) {
                    var selectedNode = Zmon.ztree.getSelectedNode();
                    if (!selectedNode || treeNode.parentNode !== selectedNode.parentNode || !treeNode.where) {
                        return false;
                    }
                },
                change: function(treeId, treeNode) {
                    $('#update').click();
                }
            }
        }, this.treeNodes);
    },
    initTimeSelect: function() {
        var $begintime = $('#begintime'), $endtime = $('#endtime');
        var timepickerSettings = {
            showSecond: true,
            dateFormat: 'yy-mm-dd',
            timeFormat: 'hh:mm:ss',
            hourGrid: 4,
            minuteGrid: 10,
            secondGrid: 10
        };
        $begintime.datetimepicker(timepickerSettings);
        $endtime.datetimepicker(timepickerSettings);
        $('#update').click(function() {
            var time_begin = $("#begintime").datetimepicker('getDate');
            var time_end = $("#endtime").datetimepicker('getDate');
            if (!time_begin || !time_end) {
                return false;
            }
            var sum_interval = 0;
            if ($('#sum_mode').attr('checked')) {
                sum_interval = $('#sum_interval').val();
            }

            var $plot = $('#plot');
            $('> div', $plot).each(function(index) {
                var chart = $(this).data('chart');
                if (chart) {
                    chart.destroy();
                }
            });
            $plot.empty();

            var selectedNode = Zmon.ztree.getSelectedNode();
            if (!selectedNode) {
                return;
            }
            var value_names = Zmon.getNodeValueNames(selectedNode) || [], names = [];
            for (var i = 0; i < value_names.length; i++) {
                if (value_names[i].divide)
                    continue;
                names.push(value_names[i].name);
            }
            for (var i = 0; i < value_names.length; i++) {
                for (var j = 0; j < names.length; j++) {
                    if (value_names[i].divide) {
                        if (value_names[i].dividend == names[j])
                            value_names[i].dividend_index = j;
                        if (value_names[i].divisor == names[j])
                            value_names[i].divisor_index = j;
                    } else {
                        if (value_names[i].name == names[j])
                            value_names[i].name_index = j;
                    }
                }
            }
            for (var i = 0; i < value_names.length; i++) {
                if (value_names[i].hidden)
                    continue;
                $('<div id="plot_div' + i + '"></div>').appendTo($plot);
            }
            var nodeKey = Zmon.getNodeKey(selectedNode), wheres = [], nodeNames = [];
            var checkedNodes = Zmon.ztree.getCheckedNodes(true);
            for (var i = 0; i < checkedNodes.length; i++) {
                wheres.push(Zmon.getNodeWhere(checkedNodes[i]));
                nodeNames.push('' + checkedNodes[i].name);
            }

            $.post('zrange', $.param({
                key: nodeKey,
                where: wheres.join('\x00'),
                value_names: names.join(','),
                time_begin: time_begin.getTime() / 1000,
                time_end: time_end.getTime() / 1000,
                sum_interval: sum_interval
            }), function(data) {
                for (var i = 0; i < value_names.length; i++) {
                    var series = [], dividend_index, divisor_index, name_index;

                    if (value_names[i].hidden)
                        continue;
                    if (value_names[i].divide) {
                        dividend_index = value_names[i].dividend_index;
                        divisor_index = value_names[i].divisor_index;

                        for (var j = 0; j < nodeNames.length; j++) {
                            series.push({
                                name: nodeNames[j],
                                pointInterval: data['interval'] * 1000,
                                pointStart: data['time_begin'] * 1000,
                                data: Zmon.divideData(data['data'][dividend_index][j], data['data'][divisor_index][j], value_names[i].percent)
                            });
                        }
                    } else {
                        name_index = value_names[i].name_index;

                        for (var j = 0; j < nodeNames.length; j++) {
                            series.push({
                                name: nodeNames[j],
                                pointInterval: data['interval'] * 1000,
                                pointStart: data['time_begin'] * 1000,
                                data: data['data'][name_index][j]
                            });
                        }
                    }
                    
                    Zmon.plotData('plot_div' + i, value_names[i], series);
                }
            }, 'json');
        });
        $('#timepicker > a').click(function(e) {
            e.preventDefault();
            var t = new Date();
            $endtime.datetimepicker('setDate', t);
            t.setTime(t.getTime() - $(this).attr('value') * 1000);
            $begintime.datetimepicker('setDate', t);
            $('#update').click();
        });
        $('#timepicker > a').first().click();
    },
    initHighcharts: function() {
        Highcharts.setOptions({
            chart: {
                type: 'line',
                borderWidth: 1,
                zoomType: 'x',
                width: 750,
            },
            credits: {
                enabled: false
            },
            global: {
                useUTC: false
            },
            legend: {
                layout: 'vertical',
                borderWidth: 0,
                width: 700,
                labelFormatter: function() {
                    var max, min, sum, count, i;
                    for (i = 0; i < this.data.length; i++) {
                        var value = this.data[i].y;
                        if (value || value == 0)
                            break;
                    }
                    if (i == this.data.length)
                        return this.name + ': max=null, min=null, avg=null';
                    max = min = sum = this.data[i].y;
                    for (count = 1, i++; i < this.data.length; i++) {
                        var value = this.data[i].y;
                        if (!value && value != 0)
                            continue;
                        if (value > max)
                            max = value;
                        if (value < min)
                            min = value;
                        sum += value;
                        count++;
                    }
                    return this.name + ': max=' + max.toFixed(2) + ', min=' + min.toFixed(2) + ', avg=' + (sum / count).toFixed(2);
                }
            },
            plotOptions: {
                line: {
                    step: true,
                    marker: {
                        enabled: false
                    },
                    lineWidth: 1,
                    shadow: false,
                    states: {
                        hover: {
                            lineWidth: 1
                        }
                    }
                },
                series: {
                    animation: false
                }
            },
            tooltip: {
                crosshairs: true,
                shared: true
            },
            xAxis: {
                type: 'datetime',
                dateTimeLabelFormats: {
                    second: '%H:%M:%S',
                    minute: '%H:%M',
                    hour: '%H:%M',
                    day: '%m-%d',
                    week: '%m-%d',
                    month: '%Y-%m',
                    year: '%Y'
                }
            },
            yAxis: {
                minPadding: 0,
                maxPadding: 0
            },
        });
    },
    getNodeKey: function(node) {
        return this.getNodeKeyByType(node, 'isKey');
    },
    getNodeListKey: function(node) {
        return this.getNodeKeyByType(node, 'isListKey');
    },
    getNodeKeyByType: function(node, keytype) {
        for (; !node[keytype] && node.parentNode; node = node.parentNode) {}
        for (var key = ''; node; node = node.parentNode) {
            key = '/' + node.name + key;
        }
        return '/zmon' + key;
    },
    getNodeWhere: function(node) {
        var where = [];
        for (; !node.isListKey && node.parentNode; node = node.parentNode) {
            if (node.where) {
                where.push(node.where.join('\x03'));
            }
        }
        //where.sort();
        where.reverse();
        return where.join('\x02');
    },
    getNodeValueNames: function(node) {
        for (; !node.valueNames && node.parentNode; node = node.parentNode) {}
        return node.valueNames || null;
    },
    getNodeDivideValueNames: function(node) {
        for (; !node.divideValueNames && node.parentNode; node = node.parentNode) {}
        return node.divideValueNames || null;
    },
    divideData: function(dividend, divisor, percent) {
        var quotient = [], q;
        for (var i = 0; i < dividend.length; i++) {
            if ((dividend[i] || dividend[i] == 0) && divisor[i]) {
                q = dividend[i] / divisor[i];
                if (percent)
                    q *= 100;
                quotient.push(q);
            } else {
                quotient.push(null);
            }
        }
        return quotient;
    },
    plotData: function(div_id, value_name, series) {
        var chart = new Highcharts.Chart({
            chart: {
                renderTo: div_id,
                height: 240 + series.length * 16
            },
            title: {
                text: value_name.name
            },
            yAxis: {
                title: {
                    text: value_name.unit
                }
            },
            series: series
        });
        $('#' + div_id).data({'chart': chart});
    }
};
