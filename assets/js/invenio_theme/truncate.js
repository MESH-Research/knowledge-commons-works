import $ from "jquery";

(function () {
  // on document ready

  // find all elements to be truncated
  document.querySelectorAll(".truncate-container").forEach((element) => {
    const textElement = element.querySelector(".truncate-text");
    const hasOverflowingText =
      textElement.scrollHeight > textElement.offsetHeight;
    if (hasOverflowingText) {
      // show Show More btn
      $(element).find(".truncate-show-more").toggle();
    }
  });

  $(".truncate-toggler").on("click", function () {
    const $container = $(this).parent(".truncate-container");

    const $text = $container.find(".truncate-text");
    const hasPreviousClass = $text.data("lines");
    if (hasPreviousClass) {
      // restore the class `truncate-<n>`
      $text.addClass(hasPreviousClass);
      $text.removeData("lines");
    } else {
      // remove the class `truncate-<n>` and save it in the data-lines attr
      const classes = $text.attr("class").split(" ");
      const cls = classes.find((cls) => cls.startsWith("truncate-lines-"));
      $text.removeClass(cls);
      $text.data("lines", cls);
    }

    // switch buttons
    $container.find(".truncate-show-more").toggle();
    $container.find(".truncate-show-less").toggle();
  });
})();
