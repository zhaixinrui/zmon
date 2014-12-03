function LoadModule(){
    //初始化"#module"中的变量
    $("#module").html("<option>模块</option>");
    $("#host").html('<option>机器名</option>');
    var data = {}
    data['product'] = $('#product').val();
    $.ajax({
        url: "/zmon/watch",
        type: "POST",
        data: data,
        dataType: "json",
        success: function(result){
		    $(result).each(function (i) {
				item = result[i];
                var str="<option value='" + item[0] + "'>" + item[1] + "</option>";
			    $("#module").append(str);
			});
        }
    });
}

function LoadHost(){
    $("#host").html('<option>机器名</option>');
    var data = {}
    data['monitorId'] = $('#module').val();
    $.ajax({
        url: "/zmon/watch",
        type: "POST",
        data: data,
        dataType: "json",
        success: function(result){
		    $(result).each(function (i) {
				item = result[i];
                var str="<option value='" + item[0] + "'>" + item[1] + "</option>";
			    $("#host").append(str);
			});
        }
    });
}
//==========websocket
var socket;
var hostip;

function connect(){
    //断开之前的连接
    close();
    //参数检查
    var req = {};
    req['username'] = $("#username").attr('value');
    req['product']  = $("#product").val();
    req['module']   = $("#module").val();
    req['host']     = $("#host").val();
    req['grep']     = $("#grep").val();
    var host = "ws://" + req['host'] + ":8112/watch";
    //建立连接
    try{
        socket = new WebSocket(host);
        socket.onopen    = function(msg){ 
            //发送请求
            var argv = $.param(req);
            send(argv);
        };
        socket.onmessage = function(msg){ 
            var res = msg.data
            $("#log").append("<p style='text-align:left;width=500px'>" + res + "</p>");
            //alert(rep); 
        };
        socket.onclose   = function(msg){ 
            //alert("Lose Connection!"); 
        };
    }
    catch(ex){ 
        alert('创建连接失败' + host); 
    }
}

function send(req){
      if(!req){ alert("Message can not be empty"); return; }
          try{ 
              socket.send(req); 
          } 
          catch(ex){ 
              alert(ex); 
          }
}

function close(){
    try{ 
        socket.send('quit'); 
        socket.close();
        socket=null;
    }
    catch(ex){ 
        //log(ex);
    }
}

window.onbeforeunload = close();

//(function($) {
//    $.websocket = function(options) {
//        var defaults = {
//            domain: top.location.hostname,
//            port:3398,
//            protocol:""
//        };
//        var opts = $.extend(defaults,options);
//        var szServer = "ws://" + opts.domain + ":" + opts.port;
//        //var szServer = "ws://" + opts.domain + ":" + opts.port + "/" + opts.protocol;
//        var socket = null;
//        var bOpen = false;
//        var t1 = 0; 
//        var t2 = 0; 
//        var messageevent = {
//            onInit:function(){
//                if(!("WebSocket" in window) && !("MozWebSocket" in window)){  
//                    return false;
//                }
//                if(("MozWebSocket" in window)){
//                    socket = new MozWebSocket(szServer);  
//                }else{
//                    socket = new WebSocket(szServer);
//                }
//                if(opts.onInit){
//                    opts.onInit();
//                }
//            },
//            onOpen:function(event){
//                bOpen = true;
//                if(opts.onOpen){
//                    opts.onOpen(event);
//                }
//            },
//            onSend:function(msg){
//                t1 = new Date().getTime(); 
//                if(opts.onSend){
//                    opts.onSend(msg);
//                }
//                socket.send(msg);
//            },
//            onMessage:function(msg){
//                t2 = new Date().getTime(); 
//                if(opts.onMessage){
//                    opts.onMessage(msg.data,t2 - t1);
//                }
//            },
//            onError:function(event){
//                if(opts.onError){
//                    opts.onError(event);
//                }
//            },
//            onClose:function(event){
//                if(opts.onclose){
//                    opts.onclose(event);
//                }
//                if(socket.close() != null){
//                    socket = null;
//                }
//            }
//        }
//
//        messageevent.onInit();
//        socket.onopen = messageevent.onOpen;
//        socket.onmessage = messageevent.onMessage;
//        socket.onerror = messageevent.onError;
//        socket.onclose = messageevent.onClose;
//        
//        this.send = function(pData){
//            if(bOpen == false){
//                return false;
//            }
//            messageevent.onSend(pData);
//            return true;
//        }
//        this.close = function(){
//            messageevent.onClose();
//        }
//        return this;
//    };
//})(jQuery);
//
//
