var socket;
var hostip;

function connect(){
    //断开之前的连接
    close();
    //参数检查
    var req = {};
    req['product'] = $("#product").val();
    req['module']  = $("#module").val();
    req['host']    = $("#host").val();
    req['grep']    = $("#grep").val();
    var host = "ws://" + req['host'] + ":8081/watch";
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
