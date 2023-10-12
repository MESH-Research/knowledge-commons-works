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

import React from 'react';
import { CitationSection } from './DetailSidebarCitationSection';
import { VersionsSection } from './DetailSidebarVersionsSection';
import { SidebarDetailsSection } from './DetailSidebarDetailsSection';

/** Mapping of sidebar section slugs to components.
 *
 * Each component is passed props from the DetailRightSidebar component
 * as specified in the "passed_args" list.
 */
const sidebarSectionComponents = {
  'versions': {"component": VersionsSection,
               "passed_args": ["isPreview", "record"]},
  'sidebar_details': {"component": SidebarDetailsSection,
                      "passed_args": ["record","doiBadgeUrl"]},
  'citation': {"component": CitationSection,
               "passed_args": ["record", "citationStyles",
                               "citationStyleDefault"]
              },
}

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
const DetailRightSidebar = (props) => {
  console.log("****DetailRightSidebar props", props);
  let activeSidebarSections = props.sidebarSections.filter(({slug}) => {
    return sidebarSectionComponents[slug] !== undefined;
  });
  return (
    <aside className="sixteen wide tablet five wide computer column right-sidebar">
      {activeSidebarSections.map(({slug}, idx) => {
        const SidebarSectionComponent = sidebarSectionComponents[slug]['component'];
        const SidebarSectionArgs = sidebarSectionComponents[slug]['passed_args'].reduce((obj, key) => { obj[key] = props[key]; return obj }, {});
        return (
          <SidebarSectionComponent {...SidebarSectionArgs} key={idx} />
        )
        }
      )}
    </aside>
  );
};

export { DetailRightSidebar };