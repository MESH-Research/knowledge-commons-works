function getFullName(nameParts) {
  let fullName = [
    getGivenName(nameParts),
    nameParts?.family_prefix,  // Follows given name in full name format
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
  if (!nameParts) return "";

  const beforeComma = getFamilyName(nameParts);
  const afterComma = [
    getGivenName(nameParts),
    nameParts?.family_prefix,  // Comes at the end in inverted format
  ]
    .filter(Boolean)
    .join(" ");

  // Only add comma if we have both parts
  if (!beforeComma || !afterComma) {
    return beforeComma || afterComma || "";
  }

  let fullNameInverted = `${beforeComma}, ${afterComma}`;
  if (nameParts?.suffix) {
    fullNameInverted += ", " + nameParts?.suffix;
  }
  return fullNameInverted;
}

function getFamilyName(nameParts) {
  // Handle family prefix fixed without space if it ends in an apostrophe
  const prefix = nameParts?.family_prefix_fixed;
  const family = nameParts?.family;

  // Special handling for prefixes ending in apostrophe (like O')
  if (prefix && family && prefix.endsWith("'")) {
    return [
      prefix + family,  // Join without space
      nameParts?.spousal,
      nameParts?.last,
    ]
      .filter(Boolean)
      .join(" ");
  }

  // Normal case with space between prefix and family
  return [
    prefix,
    nameParts?.spousal,
    family,
    nameParts?.last,
  ]
    .filter(Boolean)
    .join(" ");
}

function getGivenName(nameParts) {
  return [
    nameParts?.first,  // First name comes first
    nameParts?.given,  // Then given name
    nameParts?.middle,  // Then middle name
    nameParts?.parental,  // Then patronymic (e.g., Russian style)
    nameParts?.nickname,  // Then nickname
  ]
    .filter(Boolean)
    .join(" ");
}

// Helper function to detect if a name has a patronymic (Russian style)
function isPatronymic(nameParts) {
  // Russian patronymics typically end in -vich, -ovich, -evich for males
  // or -vna, -ovna, -evna for females
  const patronymicSuffixes = ['vich', 'ovich', 'evich', 'vna', 'ovna', 'evna'];
  return nameParts?.parental &&
    patronymicSuffixes.some(suffix =>
      nameParts.parental.toLowerCase().endsWith(suffix.toLowerCase())
    );
}

export { getFullName, getFullNameInverted, getFamilyName, getGivenName };
