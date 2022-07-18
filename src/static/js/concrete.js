//  Shape Next Button
document.getElementById("crete_shape_next").addEventListener("click", function(event) {
  var crete_shape = document.getElementById("crete_shape");
  var crete_finish = document.getElementById("crete_finish");
  crete_shape.style.display = "none";
  crete_shape.style.visibility =  "hidden";
  crete_finish.style.display = "block";
  crete_finish.style.visibility = "visible";
});

//  Shape Select onChange
document.getElementById("crete_shape_select").addEventListener("change", function(event) {
  var crete_shape_select = document.getElementById("crete_shape_select");
  var selected_shape = crete_shape_select.value
  var crete_length_labelninput = document.getElementById("crete_length_labelninput");
  var crete_width_labelninput = document.getElementById("crete_width_labelninput");
  var crete_diameter_labelninput = document.getElementById("crete_diameter_labelninput");
  if (selected_shape === "Circle") {
    crete_length_labelninput.style.display = "none";
    crete_length_labelninput.style.visibility =  "hidden";
    crete_width_labelninput.style.display = "none";
    crete_width_labelninput.style.visibility =  "hidden";
    crete_diameter_labelninput.style.display = "block";
    crete_diameter_labelninput.style.visibility = "visible";
  } else {
    crete_length_labelninput.style.display = "block";
    crete_length_labelninput.style.visibility =  "visible";
    crete_width_labelninput.style.display = "block";
    crete_width_labelninput.style.visibility =  "visible";
    crete_diameter_labelninput.style.display = "none";
    crete_diameter_labelninput.style.visibility = "hidden";
  }
});


//  Finish Previous Button
document.getElementById("crete_finish_previous").addEventListener("click", function(event) {
  var crete_finish = document.getElementById("crete_finish");
  var crete_shape = document.getElementById("crete_shape");
  crete_finish.style.display = "none";
  crete_finish.style.visibility =  "hidden";
  crete_shape.style.display = "block";
  crete_shape.style.visibility = "visible";
});

//  Finish Next Button
document.getElementById("crete_finish_next").addEventListener("click", function(event) {
  var crete_finish = document.getElementById("crete_finish");
  var crete_stamp = document.getElementById("crete_stamp");
  crete_finish.style.display = "none";
  crete_finish.style.visibility =  "hidden";
  crete_stamp.style.display = "block";
  crete_stamp.style.visibility = "visible";
});

//  Stamp Previous Button
document.getElementById("crete_stamp_previous").addEventListener("click", function(event) {
  var crete_finish = document.getElementById("crete_finish");
  var crete_stamp = document.getElementById("crete_stamp");
  crete_stamp.style.display = "none";
  crete_stamp.style.visibility =  "hidden";
  crete_finish.style.display = "block";
  crete_finish.style.visibility = "visible";
});

//  Stamp Next Button
document.getElementById("crete_stamp_next").addEventListener("click", function(event) {
  var crete_stamp = document.getElementById("crete_stamp");
  var crete_color = document.getElementById("crete_color");
  crete_stamp.style.display = "none";
  crete_stamp.style.visibility =  "hidden";
  crete_color.style.display = "block";
  crete_color.style.visibility = "visible";
});

//  Color Previous Button
document.getElementById("crete_color_previous").addEventListener("click", function(event) {
  var crete_color = document.getElementById("crete_color");
  var crete_stamp = document.getElementById("crete_stamp");
  crete_color.style.display = "none";
  crete_color.style.visibility =  "hidden";
  crete_stamp.style.display = "block";
  crete_stamp.style.visibility = "visible";
});





