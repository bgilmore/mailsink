var unreadMessages  = 0;
var messageListener = null;

jQuery.fn.extend({
  killSelection: function() {
    $(this).attr('selectable', false)
           .css('user-select', 'none')
           .css('-moz-user-select', 'none')
           .css('-webkit-user-select', 'none');
  },

  restoreSelection: function() {
    $(this).attr('selectable', true)
           .css('user-select', 'text')
           .css('-moz-user-select', 'text')
           .css('-webkit-user-select', 'text');
  }
});

function appBlur() {
  messageListener = function() {
    document.title = 'Mailsink (' + unreadMessages + ' new ' + (unreadMessages == 1 ? 'message' : 'messages') + ')';
    if (window.fluid)
      window.fluid.dockBadge = String(unreadMessages);
  }
}

function appFocus() {
  unreadMessages  = 0;
  messageListener = null;

  document.title = 'Mailsink';
  if (window.fluid)
    window.fluid.dockBadge = '';
}

function squelch(e) {
  e.preventDefault();
}

function doResize(e) {
  w   = $(document).width();
  pos = Math.max(0.25 * w, Math.min(0.50 * w, e.pageX));

  $('ul#messages').css('width', pos - 1);
  $('div#splitter').css('left', pos);
  $('div#viewer').css('left', pos + 3);
}

function startResize(e) {
  $('div#viewer').killSelection();
  $('div#dragmask').show();

  $(document).bind('mousemove', doResize)
             .bind('mouseup', endResize)
             .bind('dragstart', squelch)
             .bind('dragstop', squelch);
}

function endResize(e) {
  $('div#viewer').restoreSelection();
  $('div#dragmask').hide();

  $(document).unbind('mousemove', doResize)
             .unbind('mouseup', endResize)
             .unbind('dragstart', squelch)
             .unbind('dragstop', squelch);
}

function adjustFrame() {
  $('iframe#viewframe').height($(window).height() - $('dl#viewmeta').outerHeight());
}

function viewMessage(message) {
  var partId = null;

  $('dd#from').text(message.from);
  $('dd#subject').text(message.subject);
  $('dd#date').text(message.long_time);
  $('dd#to').text(message.to);

  /* clear select box for repop */
  $('select#part').children().remove().end();

  $(message.parts).each(function(idx, val) {
      $('<option>').val(val[0])
                   .text(val[1])
                   .appendTo($('select#part'));
  });

  /* clear old change callback and attach the new one */
  $('select#part').unbind('change')
                  .bind('change', function() {
      $('iframe#viewframe').attr('src', '/message/' + message.id + '/' + $(this).val());
  });

  /* select the first text/html or text/plain part in the list */
  $('select#part option').each(function(idx, val) {
    if ($(this).text() == 'text/html') {
      partId = $(this).val();
      return false;
    } else if ($(this).text() == 'text/plain') {
      partId = $(this).val();
    }
  });

  if (partId) {
    $('select#part').val(partId);
  } else {
    $('select#part').val($('select#part option:first').val());
  }

  $('select#part').change();

  $('.viewpane').removeClass('viewpane');
  adjustFrame(); /* re-fire in case a long field forces a line wrap */
}

function drawMessage(i, message) {
  row = $(document.createElement('li'));
  row.append("<small>" + message.short_time + "</small>")
     .append("<address>" + message.from + "</address>")
     .append("<cite>" + message.subject + "</cite>")
     .bind('click', function()
      {
        $('ul#messages li.selected').removeClass('selected');
        $(this).addClass('selected');
        viewMessage(message);
      });

  $('ul#messages').append(row);

  if (messageListener) {
    unreadMessages++;
    messageListener();
  }
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
    error: function() { 
      $('div#err').text("Error: Lost connection to server")
                  .fadeIn();
    }
  });
}

function initMessageList(messages) {
  $(messages).each(drawMessage);

  /* delay before polling to fix Chrome bug */
  window.setTimeout(poller, 500);
}

$(document).ready(function() {
  $('iframe#viewframe').attr('src', 'javascript:void(0);');

  $('ul#messages').killSelection();
  $('div#splitter').bind('mousedown', startResize);

  $(window).bind('blur', appBlur)
           .bind('focus', appFocus)
           .bind('resize', adjustFrame);

  adjustFrame();

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
