document.addEventListener("DOMContentLoaded", function () {
  document.querySelectorAll(".bollard_see_more").forEach(button => {
    button.addEventListener("click", function () {
      let row = this.closest(".bollard_content_col"); // Find the parent content container
      let hiddenContent = row.querySelector(".hidden_bollard_content");

      if (hiddenContent.style.display === "none" || hiddenContent.style.display === "") {
        hiddenContent.style.display = "block";
        this.innerText = "See Less...";
      } else {
        hiddenContent.style.display = "none";
        this.innerText = "See More...";
      }
    });
  });
});