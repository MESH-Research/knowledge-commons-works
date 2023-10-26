// This file is part of Knowledge Commons Repository
// Copyright (C) 2023 MESH Research
//
// It is modified from files provided in InvenioRDM (Invenio-App-RDM)
// Copyright (C) 2021 CERN.
// Copyright (C) 2021 Graz University of Technology.
// Copyright (C) 2021 TU Wien
//
// Knowledge Commons Repository and InvenioRDM are both free software;
// you can redistribute them and/or modify them under the terms of the MIT
// License; see LICENSE file for more details.

import React from "react";
import { i18next } from "@translations/invenio_app_rdm/i18next";
import { componentsMap } from "../componentsMap";
import { filterPropsToPass } from "../util";

const DraftBackButton = ({
  backPage,
  isPreview,
  isDraft,
  canManage,
  isPreviewSubmissionRequest,
}) => {
  return isPreview && !isPreviewSubmissionRequest && canManage && isDraft ? (
    <nav
      className="back-navigation rel-pb-2 pl-0"
      aria-label={i18next.t("Back-navigation")}
    >
      <a className="ui button labeled icon small compact" href={backPage}>
        <i className="ui icon angle left"></i> {i18next.t("Back to edit")}
      </a>
    </nav>
  ) : (
    ""
  );
};

const FlagNewerVersion = ({ isPublished, isLatest, latestHtml }) => {
  if (isPublished && !isLatest) {
    return (
      <div className="ui warning flashed top attached manage message">
        <p>
          There is a{" "}
          <a href={latestHtml}>
            <b>newer version</b>
          </a>{" "}
          of the record available.
        </p>
      </div>
    );
  } else {
    return null;
  }
};

/** Component for the right sidebar of the detail page.
 *
 * @param {object} props
 *
 * Expects the following props:
 * - sidebarSections: list of sidebar sections to display
 * - record: record to display
 * - citationStyles: list of citation styles
 * - citationStyleDefault: default citation style
 * - doiBadgeUrl: URL of the DOI badge image
 * - isPreview: whether the record is in preview mode
 * - community: community of the record
 *
 */
const DetailRightSidebar = (topLevelProps) => {
  let activeSidebarSections = topLevelProps.sidebarSectionsRight.filter(
    ({ component_name }) => {
      return (
        component_name !== undefined &&
        componentsMap[component_name] !== undefined
      );
    }
  );
  return (
    <aside className="sixteen wide tablet five wide computer column right-sidebar">
      <DraftBackButton
        backPage={topLevelProps.backPage}
        isPreview={topLevelProps.isPreview}
        isDraft={topLevelProps.isDraft}
        canManage={topLevelProps.canManage}
        isPreviewSubmissionRequest={topLevelProps.isPreviewSubmissionRequest}
      />
      <FlagNewerVersion
        isLatest={topLevelProps.record.versions.is_latest}
        isPublished={topLevelProps.record.is_published}
        latestHtml={topLevelProps.record.links.latest_html}
      />
      {activeSidebarSections.map(
        ({ section, component_name, props, subsections, show_heading }) => {
          const SidebarSectionComponent = componentsMap[component_name];
          const SidebarSectionProps = filterPropsToPass(topLevelProps, props);
          return (
            <SidebarSectionComponent
              {...SidebarSectionProps}
              section={section}
              subsections={subsections}
              key={section}
              show_heading={show_heading}
            />
          );
        }
      )}
    </aside>
  );
};

export { DetailRightSidebar };
