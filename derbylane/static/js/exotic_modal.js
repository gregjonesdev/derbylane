const selected_posts = []
let race_uuid = ""
let dogs_required = 2
let finish_order_required = false
const exotic_modal = document.getElementById("exotic-modal")


const exotic_bet_types = document.getElementById("exotic_bet_types")
const exotic_post_select = document.getElementsByClassName("exotic-post-select")
const finish_order = document.getElementById("finish-order")
const finish_order_div = document.getElementById("finish-order-div")
const submit_bet_button = document.getElementById("submit_exotic_bet")
const selected_posts_input = document.getElementById("posts-input")

exotic_modal.addEventListener("focus", function (e) {
  const button = $(event.relatedTarget) // Button that triggered the modal
  if (button.hasClass("bet-button")) {
    race_uuid = button.data('race')
    const venue = button.data('venue')
    const time = button.data('time')
    const number = button.data('number')
    const this_modal = $(this)
    this_modal.find('.modal-title').text(
      venue + " " +
      time + " Race " +
      number
    )
  }

})


handle_exotic_change = (e) => {
  finish_order_div.style.visibility = "hidden"
  submit_bet_button.disabled = true;
  select_exotic_bet(e.currentTarget.value)
  selected_posts.splice(0,8)
  update_finish_order()
  clear_selected_posts()
}

handle_select_post = (e) => {
  const currentTarget = e.currentTarget
  const post = currentTarget.value
  const is_pressed = currentTarget.getAttribute("aria-pressed")
  if (selected_posts.includes(post)) {
    const index = selected_posts.indexOf(post);
    if (index > -1) {
      selected_posts.splice(index, 1);
    }

  } else {
    selected_posts.push(post)
    if (finish_order_required) {
      finish_order_div.style.visibility = "visible"
    }
  }
  if (selected_posts.length == dogs_required) {
    toggle_posts_disable(true)
    submit_bet_button.disabled = false;
  } else {
    submit_bet_button.disabled = true;
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

exotic_modal.addEventListener("focus", function (e) {
  const button = $(event.relatedTarget) // Button that triggered the modal
  if (button.hasClass("exotic-bet")) {

    const venue = button.data('venue')
    const time = button.data('time')
    const number = button.data('number')
    const this_modal = $(this)
    this_modal.find('#bet-modalLabel').text(
      venue + " " +
      time + " Race " +
      number
    )
  }
})


handle_exotic_submit = (action) => {
  console.log("make exotic bet 79")
  if (action == 'clear') {
    // clear_bet(participant_id)
  } else if (action == 'make') {
    make_exotic_bet()
  }

}

toggle_posts_disable = (bool) => {
  for (let i=0; i<exotic_post_select.length; i++) {
    const value = exotic_post_select[i].value
    if (!selected_posts.includes(value)) {
      exotic_post_select[i].disabled = bool
    }
  }
}

clear_selected_posts = () => {
  for (let i=0; i<exotic_post_select.length; i++) {
    exotic_post_select[i].setAttribute("class", "btn btn-outline-primary exotic-post-select")
    exotic_post_select[i].ariaPressed = false
  }
  toggle_posts_disable(false)
}





select_exotic_bet = (type) => {
  switch (type) {
    case 'E':
      dogs_required = 2
      finish_order_required = true
      break;
    case 'T':
      dogs_required = 3
      finish_order_required = true
      break;
    case 'S':
      dogs_required = 4
      finish_order_required = true
      break;
    case 'Q':
    default:
      dogs_required = 2
      finish_order_required = false
  }

}


update_finish_order = () => {
  let text_content = ""
  selected_posts_list = []
  for (let i=0; i<selected_posts.length; i++) {
    text_content += selected_posts[i]
    selected_posts_list.push(selected_posts[i])
    if (i < (selected_posts.length -1)) {
      text_content += " / "
    }
    finish_order.textContent = text_content
  }
  finish_order.textContent = text_content
  selected_posts_input.value = selected_posts_list
}

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
make_exotic_bet = () => {
  let concat_posts = ""
  for (let i=0; i<selected_posts.length; i++) {
    concat_posts += selected_posts[i]
  }
  $.ajax({
    url: json_data["make_exotic_bet_url"],
    dataType: "json",
    data: {
      "amount": document.getElementById("exotic_amount_input").value,
      "race_uuid": race_uuid,
      "bet_type": document.getElementById("exotic_bet_types").value,
      "selected_posts": concat_posts
    },
    success: function(data) {
      console.log("made_ exotic bet")

      // const win_bet = data['bets']['W']
      // const place_bet = data['bets']['P']
      // const show_bet = data['bets']['S']
      //
      // const part_id = data["participant_id"]
      //
      // if (win_bet) {
      //   const target_td = document.getElementById(part_id + "-win-td")
      //   target_td.innerHTML = "";
      //   target_td.appendChild(create_button(win_bet.toFixed(2)))
      // }
      // if (place_bet) {
      //   const target_td = document.getElementById(part_id + "-place-td")
      //   target_td.innerHTML = "";
      //   target_td.appendChild(create_button(place_bet.toFixed(2)))
      //
      // }
      // if (show_bet) {
      //   const target_td = document.getElementById(part_id + "-show-td")
      //   target_td.innerHTML = "";
      //   target_td.appendChild(create_button(show_bet.toFixed(2)))
      // }
    }
  })
}
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
