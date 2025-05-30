// This file is part of InvenioRDM
// Copyright (C) 2023 CERN.
//
// InvenioRDM is free software; you can redistribute it and/or modify it
// under the terms of the MIT License; see LICENSE file for more details.

import { i18next } from "@translations/kcworks/i18next";
import React from "react";
import PropTypes from "prop-types";
import _truncate from "lodash/truncate";

import { Image, InvenioPopup } from "react-invenio-forms";
import { Icon, Label, Item, Popup } from "semantic-ui-react";
import { CommunityTypeLabel, RestrictedLabel } from "../labels";
// or from "@js/invenio_communities/community/labels";
import GeoPattern from "geopattern";

export const CommunityCompactItemComputer = ({
  result,
  actions,
  extraLabels,
  itemClassName,
  showPermissionLabel,
  detailUrl,
  isCommunityDefault,
  restrictionsMessage,
}) => {
  const { metadata, ui, links, access, id, slug } = result;
  const communityType = ui?.type?.title_l10n;

  const makePattern = (slug) => {
    return GeoPattern.generate(encodeURI(slug)).toDataUri();
  };

  return (
    <Item
      key={id}
      className={`community-item tablet computer only display-grid auto-column-grid no-wrap ${itemClassName}`}
    >
      <div className="flex align-items-center">
        <Image
          wrapped
          size="tiny"
          src={links.logo}
          alt={i18next.t("Collection logo")}
          className="community-image rel-mr-2"
          fallbackSrc={makePattern(slug)}
          onError={(e) => {
            e.target.onerror = null;
            e.target.src = makePattern(slug);
          }}
        />
        <div>
          <div className="flex align-items-center rel-mb-1">
            <a
              href={(detailUrl || links.self_html).replace('communities', 'collections')}
              className="ui small header truncate-lines-2 m-0 mr-5"
              target="_blank"
              rel="noreferrer"
              aria-label={`${metadata.title} (${i18next.t("opens in new tab")})`}
            >
              {metadata.title}
            </a>
            <i className="small icon external primary" aria-hidden="true" />
          </div>
          {metadata.description && (
            <p className="truncate-lines-1 text size small text-muted mt-5 rel-mb-1">
              {_truncate(metadata.description, { length: 50 })}
            </p>
          )}

          <div className="rel-mt-1">
            {(result.access.visibility === "restricted" ||
              communityType ||
              extraLabels) && (
              <>
                <RestrictedLabel access={access.visibility} />
                <CommunityTypeLabel type={communityType} />
                {extraLabels}
              </>
            )}
            {isCommunityDefault && (
              <Label horizontal color="purple" size="small">
                <Icon name="star" />
                {i18next.t("Primary")}
              </Label>
            )}
            {restrictionsMessage && (
              <Popup
                content={restrictionsMessage}
                trigger={
                  <Label horizontal color="red" size="small">
                    <Icon name="lock" />
                    {i18next.t("Editing restrictions")}
                  </Label>
                }
              />
            )}
          </div>
        </div>
      </div>

      <div className="flex align-items-center justify-end">
        {showPermissionLabel && (
          <span className="rel-mr-1">
            {ui?.permissions?.can_include_directly && (
              <InvenioPopup
                popupId="direct-publish-info-popup"
                size="small"
                trigger={<Icon name="paper plane outline neutral" size="large" />}
                ariaLabel={i18next.t("Submission information")}
                content={i18next.t(
                  "Submission to this community does not require review, and will be published immediately."
                )}
              />
            )}
          </span>
        )}
        {actions}
      </div>
    </Item>
  );
};

CommunityCompactItemComputer.propTypes = {
  result: PropTypes.object.isRequired,
  actions: PropTypes.node,
  extraLabels: PropTypes.node,
  itemClassName: PropTypes.string,
  showPermissionLabel: PropTypes.bool,
  detailUrl: PropTypes.string,
  isCommunityDefault: PropTypes.bool.isRequired,
  restrictionsMessage: PropTypes.string,
};

CommunityCompactItemComputer.defaultProps = {
  actions: undefined,
  extraLabels: undefined,
  itemClassName: "",
  showPermissionLabel: false,
  detailUrl: undefined,
  isCommunityDefault: false,
  restrictionsMessage: undefined,
};
