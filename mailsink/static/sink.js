function selectMessage() {
  $('ul#messages li.selected').removeClass('selected');
  $(this).addClass('selected');
}

function drawMessage(i, message) {
  row = $(document.createElement('li'));
  row.append("<small>" + message.timestamp + "</small>");
  row.append("<address>" + message.from + "</address>");
  row.append("<cite>" + message.subject + "</cite>");
  row.bind('click', selectMessage);

  $('ul#messages').append(row);
}

function poller() {
  $.ajax({
    url: '/updates.json',
    dataType: 'json',
    cache: false,
    success: function(message) { 
      if (message != null) {
        drawMessage(0, message);
      }

      poller();
    },
    error: function(x) { console.log(x); }
  });
}

function initMessageList(messages) {
  $(messages).each(drawMessage);

  /* delay before polling to fix Chrome bug */
  window.setTimeout(poller, 500);
}


function doResize(e) {
  pos = Math.max(0, e.pageX);

  $('ul#messages').css('width', pos - 1);
  $('div#splitter').css('left', pos);
  $('div#viewer').css('left', pos + 3);
}

function endResize(e) {
  $(document).unbind('mousemove', doResize)
             .unbind('mouseup', endResize);
}

function startResize(e) {
  $(document).bind('mousemove', doResize)
             .bind('mouseup', endResize);
}


$(document).ready(function() {
  $('div#splitter').bind('mousedown', startResize);

  $.ajax({
    url: '/messages.json',
    dataType: 'json',
    cache: false,
    success: initMessageList,
    error: function() {
      $('#err').show();
    }
  });
});
