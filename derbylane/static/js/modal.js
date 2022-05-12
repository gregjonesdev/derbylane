const modal = document.getElementById("bet-modal")


modal.addEventListener("focus", function (e) {
  const button = $(event.relatedTarget)

  if (button.hasClass("exotic-bet")) {
    console.log("build exotic modal")
    const venue = button.data('venue')
    const time = button.data('time')
    const number = button.data('number')
    const this_modal = $(this)
    this_modal.find('#bet-modalLabel').text(
      venue + " " +
      time + " Race " +
      number
    )
  } else {
    console.log("build straight modal")
  }
})
