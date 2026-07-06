// Part of the Knowledge Commons Repository
// Copyright (C) 2023-2026 MESH Research
//
// Alternate community selection using KCWorks' CommunityField.

import React from "react";
import Overridable from "react-overridable";
import { useStore } from "react-redux";
import { CommunityField } from "@js/kcworks/collections/selector/CommunityField";

/**
 * Community selection (no fieldPath). Same Overridable slot as stock CommunitiesComponent;
 * default child is KCWorks CommunityField instead of CommunityHeader.
 */
const CommunitiesAlternateComponent = ({
  imagePlaceholderLink = "/static/images/square-placeholder.png",
  ...extraProps
}) => {
  const record = useStore().getState().deposit?.record;
  return (
    <Overridable
      id="InvenioAppRdm.Deposit.CommunityHeader.container"
      record={record ?? {}}
      {...extraProps}
    >
      <CommunityField
        imagePlaceholderLink={imagePlaceholderLink}
        record={record ?? {}}
        {...extraProps}
      />
    </Overridable>
  );
};

/**
 * Inner field only for `InvenioAppRdm.Deposit.CommunityHeader.container` when the layout
 * still uses stock CommunitiesComponent (parent already wraps this id in Overridable).
 */
const CommunitiesAlternateField = ({ imagePlaceholderLink, ...extraProps }) => (
  <CommunityField imagePlaceholderLink={imagePlaceholderLink} {...extraProps} />
);

export { CommunitiesAlternateComponent, CommunitiesAlternateField };
