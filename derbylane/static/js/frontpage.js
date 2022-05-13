const text_content = document.getElementById("json-chart-data").textContent
const json_data = JSON.parse(text_content)

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



window.onload = (event) => {
  dropdowns = document.getElementsByClassName("dropdown-item")

  function load_races (e)  {
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
        const bets_container =   document.getElementById("bets")
        bets_container.style.maxHeight = "75vh";
        bets_container.style.overflowY = "scroll";
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
          const bets_container =   document.getElementById("bets")
          bets_container.style.maxHeight = "75vh";
          bets_container.style.overflowY = "scroll";
        }
      })

    }

  }

  load_bets()

};
