
g_request_inflight=null;

$(document).ready(function() {
  $("body").html([
    '<div id="query"><input id="q" type="text" /></div>',
    '<div id="results"></div>'
    ].join(''));

  $("#q").keydown(function(e) {

    if (g_request_inflight) {
      g_request_inflight.abort();
      g_request_inflight = null;
    }

    var q = $("#q").val();
    g_request_inflight = $.ajax({
      url: '/search',
      data: {q:q},
      error: function(xhr,status,e) {
        console.log("Error:", status, e);
        g_request_inflight = null;
      },
      success: function(data,status,xhr) {
        console.log("data:", data);
        var results = $.parseJSON(data);
        console.log("results:", results);
        //show_results(results);
        show_results([ {a: 1, b:2}, {c: 3, d:"foo"} ]);
        g_request_inflight = null;
      }
    });
    console.log($("#q").val());
  });

  $('#q').focus();
});

function show_results(rlis) {
  $('#results').empty();
  _.each(rlis, function(r) {
    var t = [];
    _.each(r, function(v,k) {
      t.push('<tr><td class="k">'+k+'</td><td width="99%">'+v+'</td></tr>');
    });
    $('#results').append('<div class="r"><table>'+t.join('')+'</table></div>');
  });
}

