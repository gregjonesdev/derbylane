const text_content = document.getElementById("json-chart-data").textContent
const json_data = JSON.parse(text_content)
const bets_container = document.getElementById("bets")
let amount = 2.0

function quickbet (e) {
  console.log("make quicky bet")
  participant = e.target.getAttribute("data-participant")
  type = e.target.getAttribute("data-type")
  $.ajax({
    url: json_data["make_bets_url"],
    dataType: "html",
    data: {
      "bet_types": type,
      "participant_id": participant,
      "amount": amount
    },
    success: function(data) {
      // $("#bets").html(data)
      console.log("success")
      parent_node = e.target.parentNode
      e.target.remove()
      parent_node.appendChild(build_button (amount.toFixed(2)))

      // document.getElementById("chart-label").textContent = label
    }
  })

}


function handle_exotic_delete (e) {
  wager_uuid = e.currentTarget.getAttribute("data-wageruuid")
  $.ajax({
    url: json_data["delete_exotic_bet_url"],
    dataType: "json",
    data: {
      "wager_uuid": wager_uuid,
    },
    success: function(data) {
      console.log(data["wager_uuid"])
      document.getElementById(data["wager_uuid"] + "-wager-div").remove()
    }
  })
}

function toggle_delete_show (e) {
  const delete_button = e.currentTarget.children.item(1);
  if (delete_button.style.display === "none") {
    delete_button.style.display = "block";
  } else {
    delete_button.style.display = "none";
  }
}

function build_button (amount) {
  const button = document.createElement("button");
  button.setAttribute("type", "button");
  button.setAttribute("class", "btn btn-sm btn-block btn-outline-light quick-bet-btn");
  button.disbled = true;
  button.textContent = amount
  return button
}

window.onload = (event) => {

  dropdowns = document.getElementsByClassName("dropdown-item")
  function load_races (e)  {
    console.log("load races")
    const currentTarget = e.currentTarget
    const label = currentTarget.textContent
    const chart_id = e.currentTarget.getAttribute("data-chart")
    load_charts(chart_id, label)




  }


  function load_charts(chart_id, label) {
    $.ajax({
      url: json_data["bets_url"],
      dataType: "html",
      data: {
        "chart_id": chart_id,
      },
      success: function(data) {
        $("#bets").html(data)
        document.getElementById("chart-label").textContent = label
      }
    })
  }

  for (let i=0; i<dropdowns.length; i++) {
    dropdowns[i].addEventListener("click", load_races)
  }



  const chart_select = document.getElementById("chart-select")

  load_bets = () => {
    console.log("load bets")
    if (chart_select) {
      chart_id = chart_select.value
      $.ajax({
        url: json_data["bets_url"],
        dataType: "html",
        data: {
          "chart_id": document.getElementById("chart-select").value,
        },
        success: function(data) {
          $("#bets").html(data)

          bets_container.style.maxHeight = "75vh";
          bets_container.style.overflowY = "scroll";
        }
      })

    }

  }


  load_bets()


};
