#!/home/space/zmon/python/bin/python
from string import Template
head = """
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
"""

foot = """	
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
                where: wheres.join('\\x00'),
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
                where.push(node.where.join('\\x03'));
            }
        }
        //where.sort();
        where.reverse();
        return where.join('\\x02');
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
"""
#window.onload = Zmon.init();
