/**
 * Scroll page to top
 */
function scrollTop() {
  window.scrollTo({
    top: 0,
    left: 0,
    behavior: "smooth",
  });
}

function moveToArrayStart(startingArray, moveTargets, keyLabel) {
  let newArray = [...startingArray];
  for ( const target of moveTargets ) {
    const index = newArray.findIndex((item) => item[keyLabel] === target);
    newArray.unshift(...newArray.splice(index, 1));
  }
  return newArray;
}

function pushToArrayEnd(startingArray, targetValue, keyLabel) {
  let newArray = [...startingArray];
  newArray.push(...newArray.splice(newArray.findIndex((item) => item[keyLabel]===targetValue), 1));
  return newArray;
}

export { scrollTop, moveToArrayStart };