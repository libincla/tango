$(document).ready( function() {
  $('#about-btn').click( function(event) {
    alert("you've clicked the button using jQuery!");
    });
  $("p").hover( function() {
    $(this).css('color', 'red');
  },
  function() {
    $(this).css('color', 'blue');
  });
});
