import React, { useState } from "react";
import { Menu, Tab } from "semantic-ui-react";
import { DetailMainTab } from "./DetailMainTab";
import { DetailRightSidebar } from "./DetailRightSidebar";
import { DetailLeftSidebar } from "./DetailLeftSidebar";
import { componentsMap } from "../componentsMap";
import { addPropsFromChildren, filterPropsToPass } from "../util";

const DetailMainTabs = (topLevelProps) => {
  const panes = topLevelProps.tabbedSections.map(
    ({ section, component_name, subsections, props, show }) => {
      // Because can't import DetailMainTab in componentsMap (circular)
      const TabComponent =
        component_name !== "DetailMainTab"
          ? componentsMap[component_name]
          : DetailMainTab;
      props = addPropsFromChildren(subsections, props);
      console.log("****DetailMainTabs props", props);
      console.log("****DetailMainTabs topLevelProps", topLevelProps);
      let passedProps =
        !!props && props.length ? filterPropsToPass(topLevelProps, props) : {};
      passedProps = {
        ...passedProps,
        section: section,
        subsections: subsections,
      };
      return {
        menuItem: (
          <Menu.Item key={section} className={show}>
            {section}
          </Menu.Item>
        ),
        render: () => (
          <Tab.Pane
            key={section}
            className={`record-details-tab ${section} ${show}`}
          >
            <TabComponent {...passedProps} key={section} />
          </Tab.Pane>
        ),
      };
    }
  );
  console.log("****DetailMainTabs panes", panes);

  return (
    <Tab
      panes={panes}
      activeIndex={topLevelProps.activeTab}
      onTabChange={(e, { activeIndex }) =>
        topLevelProps.setActiveTab(activeIndex)
      }
    />
  );
};

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

  const tabbedSections = rawProps.mainSections.filter(
    ({ component_name }) => component_name === "DetailMainTabs"
  )[0].subsections;
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

  return (
    <>
      <article className="sixteen wide tablet eleven wide computer column main-record-content">
        {rawProps.mainSections.map(
          ({ section, component_name, subsections, props, show }) => {
            const SectionComponent =
              component_name === "DetailMainTabs"
                ? DetailMainTabs
                : componentsMap[component_name];
            let passedProps;
            if (component_name === "DetailMainTabs") {
              passedProps = topLevelProps;
            } else {
              props = addPropsFromChildren(subsections, props);
              passedProps =
                !!props && props.length
                  ? filterPropsToPass(topLevelProps, props)
                  : {};
            }
            console.log("****DetailContent component_name", component_name);
            console.log("****DetailContent passedProps", passedProps);
            passedProps = {
              ...passedProps,
              activePreviewFile: activePreviewFile,
              activeTab: activeTab,
              setActivePreviewFile: setActivePreviewFile,
              setActiveTab: setActiveTab,
              section: section,
              show: show,
              tabbedSections: tabbedSections,
              subsections: subsections,
            };
            console.log("****DetailContent passedProps", passedProps);
            return <SectionComponent {...passedProps} key={section} />;
          }
        )}
      </article>
      <DetailRightSidebar
        activeTab={activeTab}
        activePreviewFile={activePreviewFile}
        {...topLevelProps}
      />
      <DetailLeftSidebar
        activeTab={activeTab}
        activePreviewFile={activePreviewFile}
        {...topLevelProps}
      />
    </>
  );
};

export { DetailContent, DetailMainTabs, filterPropsToPass };
