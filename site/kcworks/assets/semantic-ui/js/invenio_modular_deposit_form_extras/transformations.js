// Part of KCWorks, Copyright (C) MESH Research, 2023-2026
//
// KCWorks is free software; you can redistribute it and/or modify it under the
// terms of the MIT License; see LICENSE file for more details.

/**
 * @module transformations
 * @description Functions to modify the deposit for formik values before submission.
 * Each should be a pure function that accepts the values object as its one argument
 * and returns a modified copy of that object. (Do not modify the object in place.)
 * The formik state is updated all at once after all modifications have been applied,
 * in @js/invenio_modular_deposit_form/helpers/FormSubmissionTransformer. The functions
 * in the returned array are run in the array order.
 */

/**
 * Remove any empty identifier rows.
 */
function filterEmptyIdentifiers(values) {
  if (values.metadata.identifiers?.length) {
    let filteredIdentifiers = values.metadata.identifiers.reduce((newList, item) => {
      if (item.identifier !== "" && item.scheme !== "") newList.push(item);
      return newList;
    }, []);
    if (JSON.stringify(filteredIdentifiers) !== JSON.stringify(values.metadata.identifiers)) {
      return { ...values, metadata: { ...values.metadata, identifiers: filteredIdentifiers } };
    } else {
      return values;
    }
  } else {
    return values;
  }
}

/**
 * Ensure that the request protocol is stripped from ORCID ids.
 */
function fixOrcidUrl(values) {
  const orcid = values.metadata.identifiers?.filter(
    (identifier) => identifier.scheme === "orcid"
  )[0];
  if (orcid && orcid.identifier.startsWith("https://orcid.org/")) {
    const newIdentifiers = [
      ...values.metadata.identifiers.filter((identifier) => identifier.scheme !== "orcid"),
      { ...orcid, identifier: orcid.identifier.replace("https://orcid.org/", "") },
    ];
    if (JSON.stringify(newIdentifiers) !== JSON.stringify(values.metadata.identifiers)) {
      return { ...values, metadata: { ...values.metadata, identifiers: newIdentifiers } };
    } else {
      return values;
    }
  } else {
    return values;
  }
}

/**
 * Ensure publisher field is set to "Knowledge Commons" if empty.
 */
function fixEmptyPublisher(values) {
  if (!values.metadata.publisher) {
    return { ...values, metadata: { ...values.metadata, publisher: "Knowledge Commons" } };
  } else {
    return values;
  }
}

export const transformations = [filterEmptyIdentifiers, fixOrcidUrl, fixEmptyPublisher];
