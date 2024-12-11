document.addEventListener("DOMContentLoaded", () => {
    const burgerIcon = document.querySelector(".burger_icon");
    const burgerMenu = document.querySelector(".burger_menu");

    burgerIcon.addEventListener("click", () => {
        burgerMenu.classList.toggle("active");
    });
});
