import React from "react";
import PropTypes from "prop-types";

import { CommunityCompactItemComputer } from "./CommunityCompactItemComputer";
import { CommunityCompactItemMobile } from "./CommunityCompactItemMobile";
import { Trans } from "react-i18next";
import { i18next } from "@translations/i18next";
import { readableFieldLabels } from "@js/invenio_modular_deposit_form/readableFieldLabels";

/**
 * Find the fields with editing restrictions for a community
 *
 * exclude the restriction of the default community
 *
 * transform field paths to readable field labels if possible
 *
 * @param {Object} permissionsPerField - The permissions per field
 * @param {Object} currentCommunity - The current community
 * @returns {Array} The restricted fields
 */
function findRestrictedFields(permissionsPerField, currentCommunity) {
  const communityRestrictions = permissionsPerField?.[currentCommunity?.slug]?.policy;
  let allRestrictedFields = [];
  if (communityRestrictions) {
    allRestrictedFields = Array.isArray(communityRestrictions)
      ? communityRestrictions
      : Object.keys(communityRestrictions);
  }
  const restrictedFields = allRestrictedFields
    .filter(
      (field) => !field.replace("|", ".").startsWith("parent.communities.default")
    )
    .map((field) => readableFieldLabels[field] || field);
  const removalRestricted = allRestrictedFields.some((field) =>
    field.replace("|", ".").startsWith("parent.communities.default")
  );

  return [restrictedFields, removalRestricted];
}

function getRestrictionsMessage(removalRestricted, editingRestrictions) {
  return editingRestrictions.length > 0 ? (
    !removalRestricted ? (
      <Trans
        i18n={i18next}
        defaults="This collection <bold>restricts editing</bold> of the following fields on included works: <bold>{{restrictions}}</bold>"
        values={{
          restrictions: editingRestrictions.join(", "),
        }}
        components={{
          bold: <b />,
        }}
      />
    ) : (
      <Trans
        i18n={i18next}
        defaults="This collection <bold>restricts the removal</bold> of included works or changing their primary collection, and <bold>restricts editing</bold> of the following fields on included works: <bold>{{restrictions}}</bold>"
        values={{
          restrictions: editingRestrictions.join(", "),
        }}
        components={{
          bold: <b />,
        }}
      />
    )
  ) : removalRestricted ? (
    i18next.t(
      "This collection restricts the removal of included works or changing their primary collection."
    )
  ) : null;
}


const CommunityCompactItem = ({
  result,
  actions,
  extraLabels,
  itemClassName,
  showPermissionLabel,
  detailUrl,
  isCommunityDefault,
  permissionsPerField,
}) => {

  const [editingRestrictions, removalRestricted] = findRestrictedFields(
    permissionsPerField,
    result
  );
  const restrictionsMessage = getRestrictionsMessage(
    removalRestricted,
    editingRestrictions
  );
  return (
    <>
      <CommunityCompactItemComputer
        result={result}
        actions={actions}
        extraLabels={extraLabels}
        itemClassName={itemClassName}
        showPermissionLabel={showPermissionLabel}
        detailUrl={detailUrl}
        isCommunityDefault={isCommunityDefault}
        restrictionsMessage={restrictionsMessage}
      />
      <CommunityCompactItemMobile
        result={result}
        actions={actions}
        extraLabels={extraLabels}
        itemClassName={itemClassName}
        showPermissionLabel={showPermissionLabel}
        detailUrl={detailUrl}
        isCommunityDefault={isCommunityDefault}
        restrictionsMessage={restrictionsMessage}
      />
    </>
  );
}

CommunityCompactItem.propTypes = {
  result: PropTypes.object.isRequired,
  actions: PropTypes.node,
  extraLabels: PropTypes.node,
  itemClassName: PropTypes.string,
  showPermissionLabel: PropTypes.bool,
  detailUrl: PropTypes.string,
  isCommunityDefault: PropTypes.bool.isRequired,
  restrictionsMessage: PropTypes.string,
  permissionsPerField: PropTypes.object,
  removalRestricted: PropTypes.bool,
  editingRestrictions: PropTypes.array,
};

CommunityCompactItem.defaultProps = {
  actions: undefined,
  extraLabels: undefined,
  itemClassName: "",
  showPermissionLabel: false,
  detailUrl: undefined,
  isCommunityDefault: false,
  restrictionsMessage: undefined,
  permissionsPerField: undefined,
  removalRestricted: false,
  editingRestrictions: [],
};

export { CommunityCompactItem };
