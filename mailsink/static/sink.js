function selectMessage() {
  $('ul#messages li.selected').removeClass('selected');
  $(this).addClass('selected');
}

function drawMessage(i, message) {
  row = $(document.createElement('li'));
  row.append("<small>" + message.timestamp + "</small>");
  row.append("<address>" + message.from + "</address>");
  row.append("<cite>" + message.subject + "</cite>");

  $('ul#messages').append(row);
}

function initMessageList(messages) {
  $(messages).each(drawMessage);
  $('ul#messages li').bind('click', selectMessage);
}

$(document).ready(function() {
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
