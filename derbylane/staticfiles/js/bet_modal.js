make_bet = () => {
  participant_id = document.getElementById("participant_uuid").textContent
  json_data = JSON.parse(text_content)
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
      console.log("WHETRE")

      const win_bet = data['bets']['W']
      const place_bet = data['bets']['P']
      const show_bet = data['bets']['S']

      if (win_bet) {
        const target_td = document.getElementById(data["participant_id"] + "-win-td")
        target_td.appendChild(create_button(win_bet))
      }
      if (place_bet) {
        const target_td = document.getElementById(data["participant_id"] + "-place-td")
        target_td.appendChild(create_button(place_bet))

      }
      if (show_bet) {
        const target_td = document.getElementById(data["participant_id"] + "-show-td")
        target_td.appendChild(create_button(show_bet))

      }
      // span.setAttribute("style", "font-weight:bold")
      // button.appendChild(span)
      //
      // span.textContent= data["bets"]


      // $( "#bets" ).load(window.location.href);
    }
  })
}


const create_button = (text_content) => {
  button = document.createElement("button");
  button.setAttribute("type", "button");
  button.setAttribute("class", "btn btn-outline-secondary btn-block btn-sm");
  button.disabled = true;
  button.textContent = text_content;
  return button;
}
