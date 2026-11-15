document.addEventListener("DOMContentLoaded", () => {
    const year = new Date().getFullYear();
    const footer = document.querySelector("footer");
    if (footer) {
        footer.dataset.year = year;
    }
});
