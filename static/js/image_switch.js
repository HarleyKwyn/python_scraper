(function() {
  var switchImage = function() {
    locationInput = document.getElementById('location');
    htmlTag = document.getElementsByTagName('html')[0];
    if (locationInput && locationInput.value == 0) {
      htmlTag.style.backgroundImage = 'url(/static/images/YosemiteValley.jpg)';
    }
    if (locationInput && locationInput.value == 1) {
      htmlTag.style.backgroundImage = 'url(/static/images/ToulumneMeadows.jpg)';
    }
    console.log(locationInput, htmlTag);
  }
  $(document).ready(function() {
    locationInput = document.getElementById('location');
    locationInput.addEventListener('change', switchImage);
    switchImage()
  });

})();
