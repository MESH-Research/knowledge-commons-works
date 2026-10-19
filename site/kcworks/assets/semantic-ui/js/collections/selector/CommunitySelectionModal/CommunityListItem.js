// This file is part of Invenio-RDM-Records
// Copyright (C) 2020-2023 CERN.
//
// Customized for Knowledge Commons Works
// Copyright (C) 2024 Mesh Research
//
// Invenio-RDM-Records and Knowledge Commons Works are free software;
// you can redistribute and/or modify them under the terms of the MIT License;
// see LICENSE file for more details.

import { i18next } from "@translations/invenio_modular_deposit_form/i18next";
import _capitalize from "lodash/capitalize";
import PropTypes from "prop-types";
import React, { useContext } from "react";
import { Button, Icon, Label } from "semantic-ui-react";
import { CommunityCompactItem } from "@js/kcworks/collections/community/communitiesItems/CommunityCompactItem";
import { CommunityContext } from "@js/invenio_rdm_records/src/deposit/components/CommunitySelectionModal/CommunityContext";

const CommunityListItem = ({ result, permissionsPerField }) => {
  const {
    setLocalCommunity,
    getChosenCommunity,
    userCommunitiesMemberships,
    displaySelected,
  } = useContext(CommunityContext);

  const { metadata } = result;
  const itemSelected = getChosenCommunity()?.id === result.id;
  const userMembership = userCommunitiesMemberships[result["id"]];

  const actions = (
    <Button
      content={
        displaySelected && itemSelected ? i18next.t("Selected") : i18next.t("Select")
      }
      size="small"
      positive={displaySelected && itemSelected}
      onClick={() => setLocalCommunity(result)}
      aria-label={i18next.t("Select {{title}}", { title: metadata.title })}
    />
  );

  const extraLabels = userMembership && (
    <Label size="small" horizontal color="teal">
      <Icon name="key" />
      {_capitalize(userMembership)}
    </Label>
  );

  return (
    <CommunityCompactItem
      result={result}
      actions={actions}
      extraLabels={extraLabels}
      showPermissionLabel
      permissionsPerField={permissionsPerField}
    />
  );
};

CommunityListItem.propTypes = {
  result: PropTypes.object.isRequired,
  permissionsPerField: PropTypes.object,
};

CommunityListItem.defaultProps = {
  permissionsPerField: undefined,
};

export { CommunityListItem };
