make_bet = () => {
  // text_content = document.getElementById("bet-modal-data").textContent
  participant_id = document.getElementById("participant_uuid").textContent
  //console.log(participant_id)
  json_data = JSON.parse(text_content)
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
      // console.log("made_bet")
      // console.log(data)

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
