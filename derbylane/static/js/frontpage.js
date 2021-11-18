const text_content = document.getElementById("json-chart-data").textContent
const json_data = JSON.parse(text_content)



window.onload = (event) => {
  console.log("load")

  dropdowns = document.getElementsByClassName("dropdown-item")

  // function initial_load () {
  //     console.log(dropdowns[0].textContent)
  //     console.log(dropdowns[0].getAttribute("data-chart"))
  // }

  function load_races (e)  {
    console.log("load races")
    const currentTarget = e.currentTarget
    console.log(currentTarget)
    const label = currentTarget.textContent
    console.log(label)
    const chart_id = e.currentTarget.getAttribute("data-chart")
    console.log(chart_id)
    console.log(label)
    load_charts(chart_id, label)


  }

  function load_charts(chart_id, label) {
    console.log("load charts")
        $.ajax({
          url: json_data["bets_url"],
          dataType: "html",
          data: {
            "chart_id": chart_id,
          },
          success: function(data) {
            console.log("loaded charts")
            console.log(data)
            $("#bets").html(data)
            const bets_container =   document.getElementById("bets")
            bets_container.style.maxHeight = "75vh";
            bets_container.style.overflowY = "scroll";
            document.getElementById("chart-label").textContent = label
          }
        })
  }

  // initial_load()

  for (let i=0; i<dropdowns.length; i++) {
    dropdowns[i].addEventListener("click", load_races)
  }


  const chart_select = document.getElementById("chart-select")

  load_bets = () => {
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
          document.getElementById("bet-header-row").style.display="block"
        }
      })

    }

  }

  load_bets()

};
