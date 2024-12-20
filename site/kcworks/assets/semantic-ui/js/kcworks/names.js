function getFullName(nameParts) {
  let fullName = [
    getGivenName(nameParts),
    nameParts?.family_prefix,
    getFamilyName(nameParts),
  ]
    .filter(Boolean)
    .join(" ");
  if (nameParts?.suffix) {
    fullName += ", " + nameParts?.suffix;
  }
  return fullName;
}

function getFullNameInverted(nameParts) {
  const beforeComma = [
    getFamilyName(nameParts),
  ]
  const afterComma = [
    getGivenName(nameParts),
    nameParts?.family_prefix,
  ]
    .filter(Boolean)
    .join(" ");
  let fullNameInverted = `${beforeComma}, ${afterComma}`;
  if (nameParts?.suffix) {
    fullNameInverted += ", " + nameParts?.suffix;
  }
  return fullNameInverted;
}

function getFamilyName(nameParts) {
  return [
    nameParts?.family_prefix_fixed,
    nameParts?.parental,
    nameParts?.spousal,
    nameParts?.family,
    nameParts?.last,
  ]
    .filter(Boolean)
    .join(" ");
}

function getGivenName(nameParts) {
  return [
    nameParts?.given,
    nameParts?.first,
    nameParts?.middle,
    nameParts?.nickname,
  ]
    .filter(Boolean)
    .join(" ");
}

export { getFullName, getFullNameInverted, getFamilyName, getGivenName };
