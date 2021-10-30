const text_content = document.getElementById("json-chart-data").textContent


const chart_json_data = JSON.parse(text_content)
const input = document.getElementById("target_date")
const modal = document.getElementById("bet-modal")
const chart_select = document.getElementById("chart-select")

 load_bets = () => {
  if (chart_select) {
    chart_id = chart_select.value
    $.ajax({
      url: chart_json_data["bets_url"],
      dataType: "html",
      data: {
        "chart_id": chart_id,
      },
      success: function(data) {
        console.log(data)
        $("#bets").html(data)
      }
    })
  }
}
//
// input.value = input.getAttribute("data-date")
//
// handler = (e) => {
//   window.location = chart_json_data["results_url"] + "?date=" + e.target.value
// }
//
//
//
//
// modal.addEventListener("focus", function (e) {
//   var button = $(event.relatedTarget) // Button that triggered the modal
//   var participant_bets = document.getElementById("participant_bets")
//   var dog = button.data('dog')
//   var bets = button.data('bets')
//   var post = button.data('post')
//   var venue = button.data('venue')
//   var chart = button.data('chart')
//   var number = button.data('number')
//   var participant = button.data('participant')
//   var modal = $(this)
//   modal.find('.modal-subtitle').text(
//     post + " | " +
//     dog + " "
//   )
//   modal.find('.modal-title').text(
//     venue + " " +
//     chart + " Race " +
//     number
//   )
//   modal.find('#participant_uuid').text(
//     participant
//   )
//   $('select option[value=' + bets).prop('selected',true);
// })
//
//
window.onload = (event) => {

  // const text_content = document.getElementById("json-chart-data").textContent

  load_bets()

};
