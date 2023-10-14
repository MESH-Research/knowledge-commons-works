
const filterPropsToPass = (topLevelProps, propList) => {
  const passedProps = Object.keys(topLevelProps)
    .filter((key) => propList.includes(key))
    .reduce((obj, key) => {
      obj[key] = topLevelProps[key];
      return obj;
    }, {});
  return passedProps;
};

export { filterPropsToPass };