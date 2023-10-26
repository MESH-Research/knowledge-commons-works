import React, { useState } from "react";
import { Tab } from "semantic-ui-react";
import { DetailMainTab } from "./DetailMainTab";
import { DetailRightSidebar } from "./DetailRightSidebar";
import { DetailLeftSidebar } from "./DetailLeftSidebar";
import { componentsMap } from "../componentsMap";
import { addPropsFromChildren, filterPropsToPass } from "../util";

// React component for the main content of the detail page.
// This is the main content of the detail page, which includes a central
// column with the main record information, and optional left and right
// sidebars.
//
// The main column is divided into sections, which are either tabs or
// untabbed sections. These are defined in the mainSections prop which
// passes the object defined in the InvenioRDM config variable
// APP_RDM_DETAIL_MAIN_SECTIONS. Sections are displayed as tabs if they
// have a "tab" property defined with a true value.
//
// The left and right sidebars are defined in the sidebarSectionsLeft
// and sidebarSectionsRight props, which pass the objects defined in
// the InvenioRDM config variables APP_RDM_DETAIL_SIDEBAR_SECTIONS_LEFT
// and APP_RDM_DETAIL_SIDEBAR_SECTIONS_RIGHT.
//
// The config for each section includes a string with the name of the
// React component to use for the section, and a list of subsections to
// display in the section. The mapping of strings to components is
// defined in the componentsMap object in ../componentsMap.js.
//
// The props passed to each component are defined in the "props"
// property of the section config.
// Available props are:
// - backPage: URL of the previous (editing) page when previewing a draft
// - citationStyles: list of citation styles
// - citationStyleDefault: default citation style
// - community: community of the record
// - customFieldsUi: custom fields UI
// - doiBadgeUrl: URL of the DOI badge image
// - externalResources: list of external resources
// - files: list of files
// - hasPreviewableFiles: whether the record has previewable files
// - iconsRor: path to the ROR icon
// - iconsGnd: path to the GND icon
// - iconsHcUsername: path to the Humanities Commons username icon
// - iconsOrcid: path to the ORCID icon
// - isDraft: whether the record is in draft mode
// - isPreview: whether the record is in preview mode
// - isPreviewSubmissionRequest: whether the record is in preview mode
// - landingUrls: list of URLs for landing pages for various third
//     party services
// - mainSections: list of main sections to display
// - permissions: permissions for the record
// - previewFile: object with information about the default preview file
// - previewFileUrl: URL of the endpoint for file previews
// - record: record to display
// - sidebarSectionsLeft: list of left sidebar sections to display
// - sidebarSectionsRight: list of right sidebar sections to display
// - totalFileSize: total size of the files
//
// In addition, the following values are added to `props` in this component
// and are available to all components:
// - additional_descriptions: additional descriptions for the record
// - description: description of the record
// - hasFiles: whether the record has files
// - title: title of the record
// - creators: list of creators
// - contributors: list of contributors
// - canManage: whether the user can manage the record
// - showRecordManagementMenu: whether to show the record management menu
//
const DetailContent = (rawProps) => {
  const [activePreviewFile, setActivePreviewFile] = useState(
    rawProps.defaultPreviewFile
  );
  const [activeTab, setActiveTab] = useState(0);

  const untabbedSections = rawProps.mainSections.filter(
    ({ tab }) => tab === false || tab === undefined
  );
  const tabbedSections = rawProps.mainSections.filter(
    ({ tab }) => tab === true
  );
  const record = rawProps.record;
  const canManageFlag =
    rawProps.permissions !== undefined &&
    (rawProps.permissions.can_edit || rawProps.permissions.can_review);

  const extraProps = {
    activePreviewFile: activePreviewFile,
    additionalDescriptions: record.ui.additional_descriptions
      ? record.ui.additional_descriptions
      : null,
    creators: record.ui.creators,
    contributors: record.ui.contributors,
    canManage: canManageFlag,
    description: record.metadata.description,
    fileTabIndex: tabbedSections.findIndex(
      ({ section }) => section === "Files"
    ),
    hasFiles: record.files.enabled,
    previewTabIndex: tabbedSections.findIndex(({ subsections }) =>
      subsections
        .map(({ component_name }) => component_name)
        .includes("FilePreview")
    ),
    showRecordManagementMenu:
      canManageFlag &&
      (!rawProps.isPreview || rawProps.isPreviewSubmissionRequest),
    setActivePreviewFile: setActivePreviewFile,
    setActiveTab: setActiveTab,
    title: record.metadata.title,
  };
  const topLevelProps = { ...rawProps, ...extraProps };

  const panes = tabbedSections.map(
    ({ section, component_name, subsections, props }) => {
      // Because can't import DetailMainTab in componentsMap (circular)
      if (component_name === "DetailMainTab") {
        component_name = undefined;
      }
      const TabComponent =
        component_name !== undefined
          ? componentsMap[component_name]
          : DetailMainTab;
      props = addPropsFromChildren(subsections, props);
      let passedProps =
        !!props && props.length ? filterPropsToPass(topLevelProps, props) : {};
      passedProps = {
        ...passedProps,
        activePreviewFile: activePreviewFile,
        activeTab: activeTab,
        tabbedSections: tabbedSections,
        section: section,
        setActivePreviewFile: setActivePreviewFile,
        subsections: subsections,
      };
      return {
        menuItem: section,
        render: () => (
          <Tab.Pane key={section} className={`record-details-tab ${section}`}>
            <TabComponent {...passedProps} key={section} />
          </Tab.Pane>
        ),
      };
    }
  );

  return (
    <>
      <article className="sixteen wide tablet eleven wide computer column main-record-content">
        {untabbedSections.map(
          ({ section, component_name, subsections, props }) => {
            const SectionComponent = componentsMap[component_name];
            props = addPropsFromChildren(subsections, props);
            let passedProps =
              !!props && props.length
                ? filterPropsToPass(topLevelProps, props)
                : {};
            passedProps = {
              ...passedProps,
              activePreviewFile: activePreviewFile,
              setActivePreviewFile: setActivePreviewFile,
              section: section,
              tabbedSections: tabbedSections,
              subsections: subsections,
            };
            console.log("****DetailContent passedProps", passedProps);
            return <SectionComponent {...passedProps} key={section} />;
          }
        )}
        <Tab
          panes={panes}
          activeIndex={activeTab}
          onTabChange={(e, { activeIndex }) => setActiveTab(activeIndex)}
        />
      </article>
      <DetailRightSidebar
        activeTab={activeTab}
        activePreviewFile={activePreviewFile}
        backPage={topLevelProps.backPage}
        canManage={topLevelProps.canManage}
        citationStyles={topLevelProps.citationStyles}
        citationStyleDefault={topLevelProps.citationStyleDefault}
        community={topLevelProps.community}
        doiBadgeUrl={topLevelProps.doiBadgeUrl}
        files={topLevelProps.files}
        identifierSchemes={topLevelProps.identifierSchemes}
        isDraft={topLevelProps.isDraft}
        isPreview={topLevelProps.isPreview}
        isPreviewSubmissionRequest={topLevelProps.isPreviewSubmissionRequest}
        landingUrls={topLevelProps.landingUrls}
        previewFileUrl={topLevelProps.previewFileUrl}
        record={topLevelProps.record}
        setActivePreviewFile={setActivePreviewFile}
        setActiveTab={setActiveTab}
        sidebarSectionsRight={topLevelProps.sidebarSectionsRight}
        tabbedSections={tabbedSections}
        totalFileSize={topLevelProps.totalFileSize}
      />
      <DetailLeftSidebar
        citationStyles={topLevelProps.citationStyles}
        citationStyleDefault={topLevelProps.citationStyleDefault}
        community={topLevelProps.community}
        doiBadgeUrl={topLevelProps.doiBadgeUrl}
        isPreview={topLevelProps.isPreview}
        record={topLevelProps.record}
        sidebarSectionsRight={topLevelProps.sidebarSectionsRight}
      />
    </>
  );
};

export { DetailContent, filterPropsToPass };
