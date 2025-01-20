//  Burger Menu Button
document.getElementById("mobile_burger").addEventListener("click", function(event) {
  var top_nav_mobile = document.getElementById("top_nav_mobile");
  top_nav_mobile.classList.toggle('show_block');
});

// Hide mobile nav on resize 
window.addEventListener("resize", function(event){
  // console.log("window resize");
  var top_nav_mobile = document.getElementById("top_nav_mobile");
  // console.log("top nav variable added");
  var innerwidth = window.innerWidth;
  // console.log("width:" + innerwidth);
  var top_nav_display = window.getComputedStyle(top_nav_mobile).display;
  // console.log("display:" + top_nav_display);

  if (innerwidth > 768 && top_nav_display === "block") {
    // console.log("if statement true");
    top_nav_mobile.classList.remove('show_block');
  };
});

// //  Service dropdown - desktop
// document.getElementById("nav_service").addEventListener("click", function(event) {
//   // console.log("button clicked");
//   var service_dropdown = document.getElementById("service_dropdown");
//   // console.log(service_dropdown);
//   service_dropdown.classList.toggle('show_block');
// });

//  Service dropdown - mobile
document.getElementById("nav_service_mobile").addEventListener("click", function(event) {
  var service_dropdown_mobile = document.getElementById("service_dropdown_mobile");
  service_dropdown_mobile.classList.toggle('show_block');
});

//  Projects dropdown - mobile
document.getElementById("nav_project_mobile").addEventListener("click", function(event) {
  var project_dropdown_mobile = document.getElementById("project_dropdown_mobile");
  project_dropdown_mobile.classList.toggle('show_block');
});