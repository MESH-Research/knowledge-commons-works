import $ from "jquery";

const menuId = "#invenio-admin-top-nav";

/* Expand and collapse navbar  */
const toggleIcon = $("#rdm-burger-menu-icon");
const menu = $(menuId);

toggleIcon.on("click", function () {
  menu.toggleClass("active");
});

/* User profile dropdown */
$("#user-profile-dropdown.ui.dropdown").dropdown({
  showOnFocus: false,
  selectOnKeydown: false,
  action: (text, value, element) => {
    // needed to trigger navigation on keyboard interaction
    let path = element.attr("href");
    window.location.pathname = path;
  },
  onShow: () => {
    $("#user-profile-dropdown-btn").attr("aria-expanded", true);
  },
  onHide: () => {
    $("#user-profile-dropdown-btn").attr("aria-expanded", false);
  },
});

/* Burger menu */
const $burgerIcon = $("#rdm-burger-menu-icon");
const $closeBurgerIcon = $("#rdm-close-burger-menu-icon");

const handleBurgerClick = () => {
  $burgerIcon.attr("aria-expanded", true);
  $(menuId).addClass("active");
  $closeBurgerIcon.trigger("focus");
  $burgerIcon.css("display", "none");
};

const handleBurgerCloseClick = () => {
  $burgerIcon.css("display", "block");
  $burgerIcon.attr("aria-expanded", false);
  $(menuId).removeClass("active");
  $burgerIcon.trigger("focus");
};

$burgerIcon.on({ click: handleBurgerClick });
$closeBurgerIcon.on({ click: handleBurgerCloseClick });

const $invenioMenu = $("#invenio-menu");

$invenioMenu.on("keydown", (event) => {
  if (event.key === "Escape") {
    handleBurgerCloseClick();
  }
});

/* Expand and collapse side menu */

const $toggleButton = $(".side-menu-toggle");
const $leftIcon = $(".side-menu-toggle .left.icon");
const $rightIcon = $(".side-menu-toggle .right.icon");
const $sidebarMenu = $("#admin-side-menu");
const $mainContent = $("#admin-main-content");
const mainContentClassList = $mainContent[0].classList.value;

$toggleButton.on("click", () => {
  if ($mainContent.hasClass(mainContentClassList)) {
    $mainContent.removeClass(mainContentClassList).addClass("sixteen wide column");
  } else {
    $mainContent[0].classList.value = mainContentClassList; // addClass() does not add multiple of the same class, needed for responsive "wide" classes
  }

  $leftIcon.each(function () {
    $(this).toggleClass("hidden");
  });

  $rightIcon.each(function () {
    $(this).toggleClass("hidden");
  });

  $sidebarMenu.toggleClass("hidden");
});
