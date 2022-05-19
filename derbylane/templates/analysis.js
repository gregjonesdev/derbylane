colors = ["#00876c",
"#42986f",
"#68a973",
"#8cb978",
"#b0c880",
"#d3d78c",
"#f7e59b",
"#f4cc80",
"#f1b26b",
"#ed975c",
"#e77b53",
"#df5e50",
"#d43d51",]
const text_content = document.getElementById("json-chart-data").textContent
const json_data = JSON.parse(text_content)
const venue_select = document.getElementsByClassName("venue-select")

button_checks = document.getElementsByClassName("btn-check")



function get_bets(date) {
  $.ajax({
    url: json_data["get_bets_url"],
    dataType: "json",
    data: {"date": date},
    success: function(data) {
      console.log(data["venues"])


      build_chart("Profits", data["venues"], data["profits"], "chart-1")
    }
  })
}


function build_new_canvas(canvas_id) {
  new_canvas = document.createElement('canvas')
  new_canvas.setAttribute("id", canvas_id)
  new_canvas.setAttribute("style", "width:100%;max-width:600px;")
  return new_canvas
}

get_bets(document.getElementById("btnradio1").value)

function build_chart(name, x_values, y_values, div_id) {
  console.log(y_values)
  target_div = document.getElementById(div_id)
  target_div.firstElementChild.remove()
  canvas_id="chart-primo"
  new_canvas = build_new_canvas(canvas_id)
  target_div.appendChild(new_canvas)
  var barColors = ["#d62828", "#f77f00", "#fcbf49", "#eae2b7", "#003049"]
  new Chart(canvas_id, {
    type: "bar",
    data: {
      labels: x_values,
      datasets: [{
        backgroundColor: barColors,
        data: y_values
      }]
    },
    options: {
      scales: {
          // xAxes: [{
          //         display: true,
          //         scaleLabel: {
          //             display: true,
          //             labelString: 'Month'
          //         }
          //     }],
          yAxes: [{
                  display: true,
                  ticks: {
                      beginAtZero: true,
                      steps: 10,
                      stepValue: 5,
                      max: 20
                  }
              }]},
      legend: {display: false},
      title: {
        display: true,
        text: name
      }
    }
  });
}

function get_selected_date() {
    const date_select_inputs = document.getElementsByClassName("date_select_input")
    for (let i=0; i< date_select_inputs.length; i++) {
      if (date_select_inputs[i].checked) {
        return date_select_inputs[i].value
      }
    }
}

function handle_venue_select(e) {
  const target = e.currentTarget
  const venue_code = target.getAttribute("data-value");
  document.getElementById("btnGroupDrop1").textContent = target.textContent;

  console.log("here o")
  console.log()

  $.ajax({
    url: json_data["get_venue_bets_url"],
    dataType: "json",
    data: {
      "venue_code": venue_code,
      "date": get_selected_date(),
    },
    success: function(data) {
      build_chart("Profit by Bet Type", data["types"], data["profits"], "chart-1")

    }
  })

}

function handle_time_select(e) {
  console.log("triggered")
  console.log(e)


  $.ajax({
    url: json_data["get_bets_url"],
    dataType: "json",
    data: {"date": "2022-05-15"},
    success: function(data) {
      console.log("YEAH")

    }
  })

}

for (let i=0; i<button_checks.length; i++) {
  button_checks[i].addEventListener("click", handle_time_select)
}
for (let i=0; i<venue_select.length; i++) {
  venue_select[i].addEventListener("click", handle_venue_select)
}


var xValues = ["AA", "A", "B", "C"];
var yValues = [55, -49, 44, 24, 15];

const venues = ["Southland", "Tri-State", "Wheeling Downs"]

var barColors = ["#d62828", "#f77f00", "#fcbf49", "#eae2b7", "#003049"]
// new Chart("venueChart", {
//   type: "bar",
//   data: {
//     labels: venues,
//     datasets: [{
//       backgroundColor: barColors,
//       data: yValues
//     }]
//   },
//   options: {
//     legend: {display: false},
//     title: {
//       display: false,
//       text: "Venue Results"
//     }
//   }
// });

// new Chart("gradeChart", {
//   type: "bar",
//   data: {
//     labels: xValues,
//     datasets: [{
//       backgroundColor: barColors,
//       data: yValues
//     }]
//   },
//   options: {
//     legend: {display: false},
//     title: {
//       display: true,
//       text: "World Wine Production 2018"
//     }
//   }
// });
