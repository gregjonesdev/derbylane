const exotic_modal = document.getElementById("exotic-modal")
const exotic_bet_types = document.getElementById("exotic_bet_types")

exotic_modal.addEventListener("focus", function (e) {
  const button = $(event.relatedTarget) // Button that triggered the modal
  if (button.hasClass("exotic-bet")) {

    const venue = button.data('venue')
    const time = button.data('time')
    const number = button.data('number')
    console.log(button.data('participants'))

    const this_modal = $(this)
    // this_modal.find('.modal-subtitle').text(
    //   post + " | " +
    //   dog + " "
    // )
    this_modal.find('.modal-title').text(
      venue + " " +
      time + " Race " +
      number
    )

  }

})

handle_exotic_change = () => {
  console.log("Change")

}

exotic_bet_types.addEventListener("change", handle_exotic_change)

//
//
//
// handle_submit = (action) => {
//   participant_id = document.getElementById("participant_uuid").textContent
//   if (action == 'clear') {
//     clear_bet(participant_id)
//   } else if (action == 'make') {
//     make_bet(participant_id)
//   }
//
// }
//
// clear_bet = (participant_id) => {
//   $.ajax({
//     url: json_data["clear_bets_url"],
//     dataType: "json",
//     data: {
//       "participant_id": participant_id,
//     },
//     success: function(data) {
//       const part_id = data["participant_id"]
//       document.getElementById(part_id + "-win-td").innerHTML = "";
//       document.getElementById(part_id + "-place-td").innerHTML = "";
//       document.getElementById(part_id + "-show-td").innerHTML = "";}
// })
// }
//
// make_bet = (participant_id) => {
//   $.ajax({
//     url: json_data["make_bets_url"],
//     dataType: "json",
//     data: {
//       "amount": document.getElementById("amount_input").value,
//       "participant_id": participant_id,
//       "bet_types": document.getElementById("bet_types").value
//     },
//     success: function(data) {
//       // console.log("made_bet")
//
//       const win_bet = data['bets']['W']
//       const place_bet = data['bets']['P']
//       const show_bet = data['bets']['S']
//
//       const part_id = data["participant_id"]
//
//       if (win_bet) {
//         const target_td = document.getElementById(part_id + "-win-td")
//         target_td.innerHTML = "";
//         target_td.appendChild(create_button(win_bet.toFixed(2)))
//       }
//       if (place_bet) {
//         const target_td = document.getElementById(part_id + "-place-td")
//         target_td.innerHTML = "";
//         target_td.appendChild(create_button(place_bet.toFixed(2)))
//
//       }
//       if (show_bet) {
//         const target_td = document.getElementById(part_id + "-show-td")
//         target_td.innerHTML = "";
//         target_td.appendChild(create_button(show_bet.toFixed(2)))
//       }
//     }
//   })
// }
//
//
//
//
// const create_button = (text_content) => {
//   button = document.createElement("button");
//   button.setAttribute("type", "button");
//   button.setAttribute("class", "btn btn-outline-info btn-block btn-sm");
//   button.disabled = true;
//   button.textContent = text_content;
//   return button;
// }
