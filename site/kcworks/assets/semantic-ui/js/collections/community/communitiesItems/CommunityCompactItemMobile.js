// This file is part of Knowledge Commons Works
// Copyright (C) 2024-2025 Mesh Research
//
// Knowledge Commons Works is based on InvenioRDM, and
// this file is based on code from InvenioRDM. InvenioRDM is
// Copyright (C) 2022-2024 CERN.
//
// Knowledge Commons Works and InvenioRDM are both free software;
// you can redistribute and/or modify them under the terms of the
// MIT License; see LICENSE file for more details.

import { i18next } from "@translations/kcworks/i18next";
import { CommunityTypeLabel, RestrictedLabel } from "../labels";
// or from "@js/invenio_communities/community/labels";
import _truncate from "lodash/truncate";
import React from "react";
import { Image, InvenioPopup } from "react-invenio-forms";
import { Icon, Label, Popup } from "semantic-ui-react";
import PropTypes from "prop-types";
import GeoPattern from "geopattern";

const CommunityCompactItemMobile = ({
  result,
  actions,
  extraLabels,
  itemClassName,
  showPermissionLabel,
  detailUrl,
  isCommunityDefault,
  restrictionsMessage,
}) => {
  const communityType = result.ui?.type?.title_l10n;
  const { metadata, ui, links, access, id, slug } = result;

  const makePattern = (slug) => {
    return GeoPattern.generate(encodeURI(slug)).toDataUri();
  };

  return (
    <div key={id} className={`community-item mobile only ${itemClassName}`}>
      <div className="display-grid auto-column-grid no-wrap">
        <div className="flex align-items-center">
          <Image
            wrapped
            size="mini"
            src={links.logo}
            alt={i18next.t("Community logo")}
            className="community-image rel-mr-1"
            fallbackSrc={makePattern(slug)}
            onError={(e) => {
              e.target.onerror = null;
              e.target.src = makePattern(slug);
            }}
          />

          <div className="flex align-items-center rel-mb-1">
            <a
              href={detailUrl || links.self_html.replace('communities', 'collections')}
              className="ui small header truncate-lines-2 m-0 mr-5"
              target="_blank"
              rel="noreferrer"
              aria-label={`${metadata.title} (${i18next.t("opens in new tab")})`}
            >
              {metadata.title}
            </a>
            <i className="small icon external primary" aria-hidden="true" />
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
      </div>

      <div className="full-width">
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
            <Label color="purple" size="tiny">
              <Icon name="star" />
              {i18next.t("Primary")}
            </Label>
          )}
          {restrictionsMessage && (
            <Popup
              content={restrictionsMessage}
              trigger={
                <Label color="red" size="tiny">
                  <Icon name="lock" />
                  {i18next.t("Editing restrictions")}
                </Label>
              }
            />
          )}
        </div>
      </div>
    </div>
  );
};

CommunityCompactItemMobile.propTypes = {
  result: PropTypes.object.isRequired,
  extraLabels: PropTypes.node,
  itemClassName: PropTypes.string,
  showPermissionLabel: PropTypes.bool,
  actions: PropTypes.node,
  detailUrl: PropTypes.string,
  isCommunityDefault: PropTypes.bool.isRequired,
  restrictionsMessage: PropTypes.string,
};

CommunityCompactItemMobile.defaultProps = {
  actions: undefined,
  extraLabels: undefined,
  itemClassName: "",
  showPermissionLabel: false,
  detailUrl: undefined,
  restrictionsMessage: undefined,
};

export { CommunityCompactItemMobile };
