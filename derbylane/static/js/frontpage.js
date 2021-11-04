const text_content = document.getElementById("json-chart-data").textContent
json_data = JSON.parse(text_content)

make_bet = () => {
  // text_content = document.getElementById("bet-modal-data").textContent
  participant_id = document.getElementById("participant_uuid").textContent
  //console.log(participant_id)
  //console.log(json_data)
  //console.log(document.getElementById("amount_input").value)
  //console.log(json_data["make_bets_url"])
  $.ajax({
    url: json_data["make_bets_url"],
    dataType: "json",
    data: {
      "amount": document.getElementById("amount_input").value,
      "participant_id": participant_id,
      "bet_types": document.getElementById("bet_types").value
    },
    success: function(data) {
      console.log("made_bet")
      console.log(data)

      const win_bet = data['bets']['W']
      const place_bet = data['bets']['P']
      const show_bet = data['bets']['S']
      if (win_bet) {
        document.getElementById(data["participant_id"] + "-win-td").textContent = data['bets']['W']
      }
      if (place_bet) {
        document.getElementById(data["participant_id"] + "-place-td").textContent = data['bets']['P']

      }
      if (show_bet) {
        document.getElementById(data["participant_id"] + "-show-td").textContent = data['bets']['S']

      }
      // button = document.createElement("button")
      // span = document.createElement("span")
      // span.setAttribute("style", "font-weight:bold")
      // button.appendChild(span)
      //
      // button.setAttribute("class", "btn btn-sm btn-outline-success float-right")
      // span.textContent= data["bets"]


      // $( "#bets" ).load(window.location.href);
    }
  })
}

const modal = document.getElementById("bet-modal")

modal.addEventListener("focus", function (e) {
  // console.log("ok")
  // console.log($('#bet-modal').hasClass('show'))
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
    console.log("so far so good")
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
    // console.log("load bets()")

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
        }
      })

    }

  }

  load_bets()






};
