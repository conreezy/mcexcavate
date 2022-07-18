//  Shape Next Button
document.getElementById("crete_shape_next").addEventListener("click", function(event) {
  var crete_shape = document.getElementById("crete_shape");
  var crete_finish = document.getElementById("crete_finish");
  crete_shape.style.display = "none";
  crete_shape.style.visibility =  "hidden";
  crete_finish.style.display = "block";
  crete_finish.style.visibility = "visible";
});

// Shape Select
document.getElementById("crete_shape_select").addEventListener("change", function(event) {
  var crete_length_label = document.getElementById("crete_length_label");
  var crete_length_input = document.getElementById("crete_length_input");
  var crete_width_label = document.getElementById("crete_width_label");
  var crete_width_input = document.getElementById("crete_width_input");
  var crete_diameter_label = document.getElementById("crete_diameter_label");
  var crete_diameter_input = document.getElementById("crete_diameter_input");
  var crete_shape_select = document.getElementById("crete_shape_select");
  var selected_crete_shape = crete_shape_select.value

  if (selected_crete_shape === "Cirlce") {
    crete_length_label.style.display = "none";
    crete_length_label.style.visibility =  "hidden";
    crete_length_input.style.display = "none";
    crete_length_input.style.visibility =  "hidden";
    crete_width_label.style.display = "none";
    crete_width_label.style.visibility =  "hidden";
    crete_width_input.style.display = "none";
    crete_width_input.style.visibility =  "hidden";
} else {
    crete_diameter_label.style.display = "block";
    crete_diameter_input.style.visibility =  "visible";
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



