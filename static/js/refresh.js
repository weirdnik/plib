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
    var response;                                       
    var frame = document.getElementById('statuses')
    if (xmlhttp.readyState==4 && xmlhttp.status==200) {
      response = xmlhttp.responseText;
      // document.title = ''        

      if (Number(response) > 0) { 
        frame.innerHTML = response;
        if ($('#queue-counter').is(':hidden')) {
          $('#queue-counter').show(200);
        }
      }
    }
  }
                                                                                        
  xmlhttp.open('GET', url, true);
  xmlhttp.send();
}
