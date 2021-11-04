const text_content = document.getElementById("json-chart-data").textContent
json_data = JSON.parse(text_content)


const modal = document.getElementById("bet-modal")

modal.addEventListener("focus", function (e) {
  const button = $(event.relatedTarget) // Button that triggered the modal
  if (button.hasClass("bet-button")) {
    var participant_bets = document.getElementById("participant_bets")
    var dog = button.data('dog')
    var bets = button.data('bets')
    var post = button.data('post')
    var venue = button.data('venue')
    var chart = button.data('chart')
    var number = button.data('number')
    var participant = button.data('participant')
    var this_modal = $(this)
    this_modal.find('.modal-subtitle').text(
      post + " | " +
      dog + " "
    )
    this_modal.find('.modal-title').text(
      venue + " " +
      chart + " Race " +
      number
    )
    this_modal.find('#participant_uuid').text(
      participant
   )
    // $('select option[value=' + bets).prop('selected',true);
  }

})


window.onload = (event) => {



  // const chart_json_data = JSON.parse(text_content)


  const chart_select = document.getElementById("chart-select")

  load_bets = () => {
    console.log("load bets()")

    if (chart_select) {
      chart_id = chart_select.value
      // console.log(chart_id)
      // console.log(chart_json_data["bets_url"])
      $.ajax({
        url: json_data["bets_url"],
        dataType: "html",
        data: {
          "chart_id": document.getElementById("chart-select").value,
        },
        success: function(data) {
          // console.log("success 2")
          // console.log(data)
          $("#bets").html(data)
          const bets_container =   document.getElementById("bets")
          bets_container.style.maxHeight = "75vh";
          bets_container.style.overflowY = "scroll";
          document.getElementById("header-table").style.display = "block";
        }
      })

    }

  }

  load_bets()






};
