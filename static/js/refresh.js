function feed_count_check (status_id) {
  var xmlhttp;
  var url = '/status/' + status_id + '/count/';
  // remember about urls.py paths
  if (window.XMLHttpRequest)
  { // code for IE7+, Firefox, Chrome, Opera, Safari
    xmlhttp=new XMLHttpRequest();
  } else { // code for IE6, IE5
    xmlhttp=new ActiveXObject("Microsoft.XMLHTTP");
  }
                                        
  xmlhttp.onreadystatechange = function() {
                                            
    var frame = document.getElementById('statuses');
      
    if (xmlhttp.readyState==4 && xmlhttp.status==200) {
      // document.title = ''
      frame.innerHTML=xmlhttp.responseText;
    }
  }
                                                                                    
  xmlhttp.open('GET', url, true);
  xmlhttp.send();
}
