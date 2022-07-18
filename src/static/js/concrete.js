stamp1 = "Seamless Italian Slate"
stamp2 = "Castlestone"
stamp3 = "Boardwalk"

color1 = "Brown"
color2 = "Red"
color3 = "Grey"
color4 = "Black"

stamped_finish_price = 26
broom_finish_price = 12
smooth_finish_price = 12


//  Shape Select onChange
document.getElementById("crete_shape_select").addEventListener("change", function(event) {
  // hide or show length/width & diamter
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
  // Add selected shape to proj
  document.getElementById("proj_crete_shape").innerHTML = selected_shape + ", ";
  // change length, width and diameter to none
  var crete_length_input = document.getElementById("crete_length_input");
  var crete_width_input = document.getElementById("crete_width_input"); 
  var crete_diameter_input = document.getElementById("crete_diameter_input");
  crete_length_input.value = "";
  crete_width_input.value = "";
  crete_diameter_input.value = "";
  document.getElementById("proj_crete_size").innerHTML = "";
  document.getElementById("crete_total_area").innerHTML = "";
});

//  Calculate area on length input
document.getElementById("crete_length_input").addEventListener("input", function(event) {
  var crete_length_input = document.getElementById("crete_length_input"); 
  var crete_length = crete_length_input.value;
  var crete_width_input = document.getElementById("crete_width_input");
  var crete_width = crete_width_input.value;
  var crete_area = crete_width * crete_length
  document.getElementById("proj_crete_size").innerHTML = crete_area;
  document.getElementById("crete_total_area").innerHTML = "Total Area: " + crete_area + " sq ft";
  // add shape to proj area at top
  var crete_shape_select = document.getElementById("crete_shape_select");
  var selected_shape = crete_shape_select.value
  document.getElementById("proj_crete_shape").innerHTML = selected_shape + ", ";
});
//  Calculate area on width input
document.getElementById("crete_width_input").addEventListener("input", function(event) {
  var crete_length_input = document.getElementById("crete_length_input"); 
  var crete_length = crete_length_input.value;
  var crete_width_input = document.getElementById("crete_width_input");
  var crete_width = crete_width_input.value;
  var crete_area = crete_width * crete_length
  document.getElementById("proj_crete_size").innerHTML = crete_area;
  document.getElementById("crete_total_area").innerHTML = "Total Area: " + crete_area + " sq ft";
  // add shape to proj area at top
  var crete_shape_select = document.getElementById("crete_shape_select");
  var selected_shape = crete_shape_select.value
  document.getElementById("proj_crete_shape").innerHTML = selected_shape + ", ";
});
//  Calculate area on diameter input
document.getElementById("crete_diameter_input").addEventListener("input", function(event) {
  var crete_diameter_input = document.getElementById("crete_diameter_input"); 
  var crete_diameter = crete_diameter_input.value;
  var crete_area = ((crete_diameter / 2) * (crete_diameter / 2) * 3.14159265359).toFixed(2);
  document.getElementById("proj_crete_size").innerHTML = crete_area;
  document.getElementById("crete_total_area").innerHTML = "Total Area: " + crete_area + " sq ft";
  // add shape to proj area at top
  var crete_shape_select = document.getElementById("crete_shape_select");
  var selected_shape = crete_shape_select.value
  document.getElementById("proj_crete_shape").innerHTML = selected_shape + ", ";
});

//  Shape Next Button
document.getElementById("crete_shape_next").addEventListener("click", function(event) {
  var crete_shape = document.getElementById("crete_shape");
  var crete_finish = document.getElementById("crete_finish");
  crete_shape.style.display = "none";
  crete_shape.style.visibility =  "hidden";
  crete_finish.style.display = "block";
  crete_finish.style.visibility = "visible";
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

//  Stamped Finish Button
document.getElementById("stamped_finish").addEventListener("click", function(event) {
  // Go to next page (stamp)
  var crete_finish = document.getElementById("crete_finish");
  var crete_stamp = document.getElementById("crete_stamp");
  crete_finish.style.display = "none";
  crete_finish.style.visibility =  "hidden";
  crete_stamp.style.display = "block";
  crete_stamp.style.visibility = "visible";
  // add finish choice to proj
  document.getElementById("proj_crete_finish").innerHTML = ", Stamped, ";
});

// Broom Finish Button
document.getElementById("broom_finish").addEventListener("click", function(event) {
  // Hide Finish Page (stamp)
  var crete_finish = document.getElementById("crete_finish");
  crete_finish.style.display = "none";
  crete_finish.style.visibility =  "hidden";
  // Show Price Page (stamp)
  var crete_price = document.getElementById("crete_price");
  crete_price.style.display = "block";
  crete_price.style.visibility =  "visible";
  // Show price details
  var broom_price_details = document.getElementById("broom_price_details");
  broom_price_details.style.display = "block";
  broom_price_details.style.visibility =  "visible";
  // add finish choice to proj
  document.getElementById("proj_crete_finish").innerHTML = ", Broom, ";
  // calculate and add price to proj
  var square_feet = document.getElementById("proj_crete_size").innerHTML;
  document.getElementById("proj_crete_price").innerHTML = "Price: $" + (square_feet * broom_finish_price).toFixed(2);
});

//  Smooth Finish Button
document.getElementById("smooth_finish").addEventListener("click", function(event) {
  // Home finish page
  var crete_finish = document.getElementById("crete_finish");
  crete_finish.style.display = "none";
  crete_finish.style.visibility =  "hidden";
  // Show Price Page (stamp)
  var crete_price = document.getElementById("crete_price");
  crete_price.style.display = "block";
  crete_price.style.visibility =  "visible";
  // Show price details
  var smooth_price_details = document.getElementById("smooth_price_details");
  smooth_price_details.style.display = "block";
  smooth_price_details.style.visibility =  "visible";
  // add finish choice to proj
  document.getElementById("proj_crete_finish").innerHTML = ", Smooth, ";
  // calculate and add price to proj
  var square_feet = document.getElementById("proj_crete_size").innerHTML;
  document.getElementById("proj_crete_price").innerHTML = "Price: $" + (square_feet * smooth_finish_price).toFixed(2);
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

//  Stamp Option 1 Button
document.getElementById("stamp_option_1").addEventListener("click", function(event) {
  var crete_stamp = document.getElementById("crete_stamp");
  var crete_color = document.getElementById("crete_color");
  crete_stamp.style.display = "none";
  crete_stamp.style.visibility =  "hidden";
  crete_color.style.display = "block";
  crete_color.style.visibility = "visible";
  // add stamp choice to proj
  document.getElementById("proj_crete_stamp").innerHTML = stamp1 +", ";
});

//  Stamp Option 2 Button
document.getElementById("stamp_option_2").addEventListener("click", function(event) {
  var crete_stamp = document.getElementById("crete_stamp");
  var crete_color = document.getElementById("crete_color");
  crete_stamp.style.display = "none";
  crete_stamp.style.visibility =  "hidden";
  crete_color.style.display = "block";
  crete_color.style.visibility = "visible";
  // add stamp choice to proj
  document.getElementById("proj_crete_stamp").innerHTML = stamp2 +", ";
});

//  Stamp Option 3 Button
document.getElementById("stamp_option_3").addEventListener("click", function(event) {
  var crete_stamp = document.getElementById("crete_stamp");
  var crete_color = document.getElementById("crete_color");
  crete_stamp.style.display = "none";
  crete_stamp.style.visibility =  "hidden";
  crete_color.style.display = "block";
  crete_color.style.visibility = "visible";
  // add stamp choice to proj
  document.getElementById("proj_crete_stamp").innerHTML = stamp3 +", ";
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

//  Color Option 1 Button
document.getElementById("color_option_1").addEventListener("click", function(event) {
  // hide color page
  var crete_color = document.getElementById("crete_color");
  crete_color.style.display = "none";
  crete_color.style.visibility =  "hidden";
  // Show Price Page
  var crete_price = document.getElementById("crete_price");
  crete_price.style.display = "block";
  crete_price.style.visibility =  "visible";
  // Show price details
  var stamped_price_details = document.getElementById("stamped_price_details");
  stamped_price_details.style.display = "block";
  stamped_price_details.style.visibility =  "visible";
  // add stamp choice to proj
  document.getElementById("proj_crete_color").innerHTML = color1;
  // calculate and add price to proj
  var square_feet = document.getElementById("proj_crete_size").innerHTML;
  document.getElementById("proj_crete_price").innerHTML = "Price: $" + (square_feet * stamped_finish_price).toFixed(2);
});

//  Color Option 2 Button
document.getElementById("color_option_2").addEventListener("click", function(event) {
  // hide color page
  var crete_color = document.getElementById("crete_color");
  crete_color.style.display = "none";
  crete_color.style.visibility =  "hidden";
  // Show Price Page
  var crete_price = document.getElementById("crete_price");
  crete_price.style.display = "block";
  crete_price.style.visibility =  "visible";
  // Show price details
  var stamped_price_details = document.getElementById("stamped_price_details");
  stamped_price_details.style.display = "block";
  stamped_price_details.style.visibility =  "visible";
  // add stamp choice to proj
  document.getElementById("proj_crete_color").innerHTML = color2;
  // calculate and add price to proj
  var square_feet = document.getElementById("proj_crete_size").innerHTML;
  document.getElementById("proj_crete_price").innerHTML = "Price: $" + (square_feet * stamped_finish_price).toFixed(2);
});

//  Color Option 3 Button
document.getElementById("color_option_3").addEventListener("click", function(event) {
  // hide color page
  var crete_color = document.getElementById("crete_color");
  crete_color.style.display = "none";
  crete_color.style.visibility =  "hidden";
  // Show Price Page
  var crete_price = document.getElementById("crete_price");
  crete_price.style.display = "block";
  crete_price.style.visibility =  "visible";
  // Show price details
  var stamped_price_details = document.getElementById("stamped_price_details");
  stamped_price_details.style.display = "block";
  stamped_price_details.style.visibility =  "visible";
  // add stamp choice to proj
  document.getElementById("proj_crete_color").innerHTML = color3;
  // calculate and add price to proj
  var square_feet = document.getElementById("proj_crete_size").innerHTML;
  document.getElementById("proj_crete_price").innerHTML = "Price: $" + (square_feet * stamped_finish_price).toFixed(2);
});

//  Color Option 4 Button
document.getElementById("color_option_4").addEventListener("click", function(event) {
  // hide color page
  var crete_color = document.getElementById("crete_color");
  crete_color.style.display = "none";
  crete_color.style.visibility =  "hidden";
  // Show Price Page
  var crete_price = document.getElementById("crete_price");
  crete_price.style.display = "block";
  crete_price.style.visibility =  "visible";
  // Show price details
  var stamped_price_details = document.getElementById("stamped_price_details");
  stamped_price_details.style.display = "block";
  stamped_price_details.style.visibility =  "visible";
  // add stamp choice to proj
  document.getElementById("proj_crete_color").innerHTML = color4;
  // calculate and add price to proj
  var square_feet = document.getElementById("proj_crete_size").innerHTML;
  document.getElementById("proj_crete_price").innerHTML = "Price: $" + (square_feet * stamped_finish_price).toFixed(2);
});



