/*
 * This file is part of Knowledge Commons Works.
 * Copyright (C) 2024 Mesh Research.
 *
 * Knowledge Commons Works is built on InvenioRDM
 * Copyright (C) 2016-2021 CERN.
 * Copyright (C) 2023 Northwestern University.
 *
 * Knowledge Commons Works and Invenio are free software; you can redistribute
 * it and/or modify them under the terms of the MIT License; see LICENSE file
 * for more details.
 */

import React from "react";
import ReactDOM from "react-dom";
import i18next from "i18next";
import { Image } from "react-invenio-forms";
import { AccessStatusLabel } from "./labels/AccessStatusLabel";
import Geopattern from "geopattern";
import { PropTypes } from "prop-types";

const CommunityDetailsHeader = ({
  communityLogoUrl,
  communityTitle,
  communityType,
  organizations,
  rorIconUrl,
  slug,
  visibility,
  website
}) => {
  let pattern = '';
  console.log("logo", communityLogoUrl);

  // user dynamic placeholder pattern in place of vanilla placeholder image
  if (["/static/images/square-placeholder.png", undefined, null].includes(communityLogoUrl)) {
    pattern = Geopattern.generate(slug);

    // use rgba version of svg pattern color for header background
    const opacity = 0.1;
    const values = pattern.color.match(/\w\w/g);
    const [r, g, b] = values.map((k) => parseInt(k, 16))

    document.getElementsByClassName("page-subheader-outer")[0].style.backgroundColor = `rgba( ${r}, ${g}, ${b}, ${opacity} )`;
  }

  return (
    <div className="sixteen wide mobile sixteen wide tablet thirteen wide computer column">
      <div className="community-header flex align-items-center column-mobile align-items-start-mobile">
        <div className="flex align-items-center">
          <div className="ui rounded image community-image mt-5 rel-mr-2">
            <Image
              src={communityLogoUrl !== "/static/images/square-placeholder.png" ? communityLogoUrl : '/static/images/square-placeholder-fake.png'}
              alt={`logo for ${communityTitle} collection`}
              className="rel-mb-1"
              fallbackSrc={pattern !== '' ? pattern.toDataUri() : ''}
            />
          </div>

          <div className="mobile only">
            <h1 className="ui medium header mb-5">{communityTitle}</h1>
          </div>
        </div>

        <div>
          <div className="flex align-items-center mb-5 tablet computer only">
            <h1 className="ui medium header mb-0">{communityTitle}</h1>

            {visibility == "restricted" && (
              <div className="rel-ml-1">
                <AccessStatusLabel />
              </div>
            )}
          </div>

          <div>
            {visibility == "restricted" && (
              <div className="mobile only rel-mb-1">
                <AccessStatusLabel />
              </div>
            )}

            {website && (
              <div className="inline-computer mt-5 rel-mr-1">
                <i className="linkify icon" aria-hidden="true"></i>
                <a href={website}>
                  {website}
                </a>
              </div>
            )}

            {communityType && (
              <div className="inline-computer mt-5 rel-mr-1">
                <i className="tag icon" aria-hidden="true"></i>
                <span className="label label-keyword">
                  {communityType}
                </span>
              </div>
            )}

            {organizations &&
              organizations.map((org, idx) => (
                <div className="inline-computer mt-5"
                  key={idx}
                >
                  {idx == 0 && (
                    <i className="building outline icon" aria-hidden="true"></i>
                  )}

                  {org.name}

                  {org.id && (
                    <a
                      href={`https://ror.org/${org.id}`}
                      aria-label={`${org.name}'s ROR ${i18next.t("profile")}`}
                      title={`${org.name}'s ROR ${i18next.t("profile")}`}
                      target="_blank"
                    >
                      <img className="inline-id-icon" src={rorIconUrl} alt="" />
                    </a>
                  )}
                  {idx == organizations.length - 2 && ", "}
                </div>
              ))}
          </div>
        </div>
      </div>
    </div>
  );
};

CommunityDetailsHeader.propTypes = {
  communityLogoUrl: PropTypes.string,
  communityTitle: PropTypes.string.isRequired,
  communityType: PropTypes.string,
  organizations: PropTypes.array,
  rorIconUrl: PropTypes.string.isRequired,
  slug: PropTypes.string.isRequired,
  // visibility: PropTypes.string,
  website: PropTypes.string,
};


document.addEventListener("DOMContentLoaded", () => {
  const headerContainer = document.getElementById("community-detail-header");

  console.log("headerContainer", headerContainer);
  console.log("headerContainer.dataset", headerContainer.dataset);

  const communityLogoUrl = headerContainer.dataset.communityLogoUrl;
  const communityTitle = headerContainer.dataset.communityTitle;
  const communityType = headerContainer.dataset.communityType;
  const organizations = JSON.parse(headerContainer.dataset.organizations);
  const rorIconUrl = headerContainer.dataset.rorIconUrl;
  const slug = headerContainer.dataset.slug;
  const visibility = headerContainer.dataset.visibility;
  const website = headerContainer.dataset.website;


  if (headerContainer) {

    ReactDOM.render(
      <CommunityDetailsHeader
        communityLogoUrl={communityLogoUrl}
        communityTitle={communityTitle}
        communityType={communityType}
        organizations={organizations}
        rorIconUrl={rorIconUrl}
        slug={slug}
        visibility={visibility}
        website={website}
      />,
      headerContainer
    );
  }
});


export { CommunityDetailsHeader };
