const rorValidator = function (val) {
  // Test if argument is a ROR ID.
  const rorRegexp = new RegExp(
    "(?:https?://)?(?:ror\\.org/)?(0\\w{6}\\d{2})$",
    "i"
  );
  // See https://ror.org/facts/#core-components.
  return rorRegexp.test(val);
};

export { rorValidator };
