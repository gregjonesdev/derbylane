const exotic_modal = document.getElementById("exotic-modal")
const exotic_bet_types = document.getElementById("exotic_bet_types")
const exotic_post_select = document.getElementsByClassName("exotic-post-select")
const finish_order = document.getElementById("finish-order")
const selected_posts = []
exotic_modal.addEventListener("focus", function (e) {
  const button = $(event.relatedTarget) // Button that triggered the modal
  if (button.hasClass("exotic-bet")) {

    const venue = button.data('venue')
    const time = button.data('time')
    const number = button.data('number')

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


toggle_posts_disable = (bool) => {
  for (let i=0; i<exotic_post_select.length; i++) {
    const value = exotic_post_select[i].value
    if (!selected_posts.includes(value)) {
      exotic_post_select[i].disabled = bool
    }
  }
}


handle_exotic_change = (e) => {
  console.log("Change")
  console.log(e.currentTarget.value)

}


update_finish_order = () => {
  console.log("hey")
  let text_content = ""
  for (let i=0; i<selected_posts.length; i++) {
    text_content += selected_posts[i]
    if (i < (selected_posts.length -1)) {
      text_content += " / "
    }
    finish_order.textContent = text_content
  }
  finish_order.textContent = text_content
}

handle_select_post = (e) => {
  console.log("Select Post")
  console.log(e.currentTarget.value)
  const currentTarget = e.currentTarget
  const post = currentTarget.value
  const is_pressed = currentTarget.getAttribute("aria-pressed")
  if (selected_posts.includes(post)) {
    const index = selected_posts.indexOf(post);
    if (index > -1) {
      selected_posts.splice(index, 1);
    }

  } else {
  //   // if false, add to list
    selected_posts.push(post)
    console.log("not pressed")


  //   console.log(selected_posts.index(post))
  }
  if (selected_posts.length >= 2) {
    toggle_posts_disable(true)
  } else {
    toggle_posts_disable(false)
  }
  update_finish_order()
  // if (e.currentTarget.value == "4") {
  //   disable_remaining_posts()
  // }
}




exotic_bet_types.addEventListener("change", handle_exotic_change)

for (let i=0; i<exotic_post_select.length; i++) {
  exotic_post_select[i].addEventListener("click", handle_select_post)
}
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
