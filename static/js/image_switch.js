;(function() {
  var switchImage = function() {
    locationInput = document.getElementById('location')
    // Match this order with the order of location options in input
    bgs = [document.getElementById('yos'), document.getElementById('tou')]
    locationInput &&
      bgs.forEach(function(el, i) {
        if (el) {
          el.style.opacity = i === parseInt(locationInput.value) ? 1 : 0
        }
      })
  }
  $(document).ready(function() {
    locationInput = document.getElementById('location')
    locationInput.addEventListener('change', switchImage)
    try {
      switchImage()
    } catch (e) {
      console.warn(e)
    }
  })
})()
