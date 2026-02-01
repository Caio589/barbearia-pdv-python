function showPage(pageId) {
  const pages = document.querySelectorAll(".page");

  pages.forEach(p => {
    p.style.display = "none";
  });

  const page = document.getElementById(pageId);
  if (page) {
    page.style.display = "block";
  }
}

window.onload = function () {
  showPage("pdv");
};
