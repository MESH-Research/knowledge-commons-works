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
import { i18next } from "@translations/invenio_rdm_records/i18next";
import { Image } from "react-invenio-forms";
import { AccessStatusLabel } from "./labels/AccessStatusLabel";
import Geopattern from "geopattern";
import { PropTypes } from "prop-types";

const CommunityDetailsHeader = ({
  activeMenuItem,
  canModerate,
  canRead,
  canSearchRequests,
  canUpdate,
  communityLogoUrl,
  communityTitle,
  communityType,
  hasCurationPolicyContent,
  hasAboutContent,
  organizations,
  rorIconUrl,
  slug,
  visibility,
  website,
}) => {
  let pattern = "";
  console.log("logo", communityLogoUrl);

  // user dynamic placeholder pattern in place of vanilla placeholder image
  if (
    ["/static/images/square-placeholder.png", undefined, null].includes(
      communityLogoUrl
    )
  ) {
    pattern = Geopattern.generate(slug);

    // use rgba version of svg pattern color for header background
    const opacity = 0.1;
    const values = pattern.color.match(/\w\w/g);
    const [r, g, b] = values.map((k) => parseInt(k, 16));

    document.getElementsByClassName(
      "page-subheader-outer"
    )[0].style.backgroundColor = `rgba( ${r}, ${g}, ${b}, ${opacity} )`;
  }

  let all_menu_items = [
    {
      name: "search",
      text: "Works",
      icon: "file alternate",
      permissions: canRead,
      url: `/collections/${slug}`,
    },
    {
      name: "members",
      text: "Members",
      icon: "users",
      permissions: canRead,
      url: `/collections/${slug}/members`,
    },
    {
      name: "requests",
      text: "Requests",
      icon: "inbox",
      permissions: canSearchRequests,
      url: `/collections/${slug}/requests`,
    },
    {
      name: "settings",
      text: "Settings",
      icon: "settings",
      permissions: canUpdate,
      url: `/collections/${slug}/settings`,
    },
  ];
  if (!!hasCurationPolicyContent) {
    all_menu_items = [
      ...all_menu_items.slice(0, 1),
      {
        name: "curation_policy",
        text: "Curation policy",
        icon: "balance scale",
        permissions: canRead,
        url: `/collections/${slug}/curation-policy`,
      },
      ...all_menu_items.slice(1),
    ];
  }
  if (!!hasAboutContent) {
    all_menu_items = [
      {
        name: "about",
        text: "About",
        icon: "info",
        permissions: canRead,
        url: `/collections/${slug}/about`,
      },
      ...all_menu_items,
    ];
  }
  console.log("canRead", canRead);
  console.log("canSearchRequests", canSearchRequests);
  console.log("canUpdate", canUpdate);
  console.log("canModerate", canModerate);
  const menu_items = all_menu_items.filter((item) => !!item.permissions);
  console.log("menu_items", menu_items);

  return (
    <div class="ui container relaxed grid page-subheader mr-0-mobile ml-0-mobile">
      <div className="row pb-0">
        <div className="sixteen wide mobile sixteen wide tablet thirteen wide computer column">
          <div className="community-header flex align-items-center column-mobile align-items-start-mobile">
            <div className="flex align-items-center">
              <div className="ui rounded image community-image mt-5 rel-mr-2">
                <Image
                  src={
                    communityLogoUrl !==
                    "/static/images/square-placeholder.png"
                      ? communityLogoUrl
                      : "/static/images/square-placeholder-fake.png"
                  }
                  alt={`logo for ${communityTitle} collection`}
                  className="rel-mb-1"
                  fallbackSrc={pattern !== "" ? pattern.toDataUri() : ""}
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
                    <a href={website}>{website}</a>
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
                    <div className="inline-computer mt-5" key={idx}>
                      {idx == 0 && (
                        <i
                          className="building outline icon"
                          aria-hidden="true"
                        ></i>
                      )}

                      {org.name}

                      {org.id && (
                        <a
                          href={`https://ror.org/${org.id}`}
                          aria-label={`${org.name}'s ROR ${i18next.t(
                            "profile"
                          )}`}
                          title={`${org.name}'s ROR ${i18next.t("profile")}`}
                          target="_blank"
                        >
                          <img
                            className="inline-id-icon"
                            src={rorIconUrl}
                            alt=""
                          />
                        </a>
                      )}
                      {idx <= organizations.length - 2 && <span>,&nbsp;</span>}
                    </div>
                  ))}
              </div>
            </div>
          </div>
        </div>
        <div className="sixteen wide mobile sixteen wide tablet three wide computer right aligned column">
          <a
            href={`/uploads/new?community=${slug}`}
            className="ui positive button labeled icon rel-mt-1 theme-secondary"
          >
            <i className="upload icon" aria-hidden="true"></i>
            {i18next.t("Contribute a work")}
          </a>
          {canModerate && (
            <a
              href={`/administration/communities?q=slug:${slug}`}
              className="ui button labeled icon rel-mt-1"
            >
              <i className="cog icon" aria-hidden="true"></i>
              {i18next.t("Manage collection")}
            </a>
          )}
        </div>
      </div>

      <div className="ui divider mobile only"></div>

      <div className="ui container secondary pointing stackable menu page-subheader pl-0 pr-0 theme-primary">
        {menu_items.map((item) => (
          <a
            className={`item ${
              activeMenuItem === item.name ||
              (activeMenuItem === "search" && item.name === "records")
                ? "active"
                : ""
            }`}
            href={item.url}
          >
            <i aria-hidden="true" className={`${item.icon} icon`}></i>
            {item.text}
          </a>
        ))}
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
  visibility: PropTypes.string,
  website: PropTypes.string,
};

// TODO: for some reason the container element wasn't being found by
// the querySelector
document.addEventListener("DOMContentLoaded", () => {
  const headerContainer = document.getElementById("community-detail-header");

  console.log("headerContainer.dataset", headerContainer.dataset);

  const activeMenuItem = headerContainer.dataset.activeMenuItem;
  const canModerate =
    headerContainer.dataset.canModerate === "True" ? true : false;
  const canRead = headerContainer.dataset.canRead === "True" ? true : false;
  const canSearchRequests =
    headerContainer.dataset.canSearchRequests === "True" ? true : false;
  const canUpdate =
    headerContainer.dataset.canUpdate === "True" ? true : false;
  const communityLogoUrl = headerContainer.dataset.communityLogoUrl;
  const communityTitle = headerContainer.dataset.communityTitle;
  const communityType = headerContainer.dataset.communityType;
  const hasCurationPolicyContent =
    headerContainer.dataset.hasCurationPolicyContent;
  const hasAboutContent = headerContainer.dataset.hasAboutContent;
  const organizations = JSON.parse(headerContainer.dataset.organizations);
  const rorIconUrl = headerContainer.dataset.rorIconUrl;
  const slug = headerContainer.dataset.slug;
  const visibility = headerContainer.dataset.visibility;
  const website = headerContainer.dataset.website;

  if (headerContainer) {
    ReactDOM.render(
      <CommunityDetailsHeader
        canModerate={canModerate}
        canRead={canRead}
        canSearchRequests={canSearchRequests}
        canUpdate={canUpdate}
        communityLogoUrl={communityLogoUrl}
        communityTitle={communityTitle}
        communityType={communityType}
        organizations={organizations}
        rorIconUrl={rorIconUrl}
        slug={slug}
        visibility={visibility}
        website={website}
        hasCurationPolicyContent={hasCurationPolicyContent}
        hasAboutContent={hasAboutContent}
        activeMenuItem={activeMenuItem}
      />,
      headerContainer
    );
  }
});

export { CommunityDetailsHeader };
