
$(document).ready(function() {
  $("body").html([
    '<div id="query"><input id="q" type="text" /></div>',
    '<div id="results"></div>'
    ].join(''));

  $("#q").keydown(function(e) {
    var q = $("#q").val();
    $.ajax({
      url: '/search',
      data: {q:q},
      error: function(xhr,status,e) { console.log("Error:", status, e); },
      success: function(data,status,xhr) {
        console.log("data:", data);
        var results = $.parseJSON(data);
        console.log("results:", results);
        //show_results(results);
        show_results([ {a: 1, b:2}, {c: 3, d:"foo"} ]);
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

