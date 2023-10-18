import React from "react";
import { i18next } from "@translations/invenio_app_rdm/i18next";
import { componentsMap } from "../componentsMap";
import { filterPropsToPass } from "../util";

/**
 * Component for the default content section (tab) of the record detail page.
 *
 * @component
 * @param {} param0
 * @returns
 */
// community,
// customFieldsUi,
// externalResources,
// previewFileUrl,
// files,
// hasFiles,
// hasPreviewableFiles,
// iconsRor,
// iconsGnd,
// iconsHcUsername,
// iconsOrcid,
// isDraft,
// isPreview,
// landingUrls,
// subSections,
// record,
// permissions,
// previewFile,
// sidebarSections,
// totalFileSize
const DetailMainTab = (topLevelProps) => {
  console.log("****DetailMainTab component topLevelProps", topLevelProps);
  return (
    <>
      {!!topLevelProps.subsections.length &&
        topLevelProps.subsections.map(
          ({ section, component_name, subsections, props }, idx) => {
            const SubSectionComponent = componentsMap[component_name];
            return (
              <section
                id={`${section}-tab-section`}
                className="rel-mt-0"
                aria-label={i18next.t(section)}
                key={idx}
              >
                <SubSectionComponent
                  {...filterPropsToPass(topLevelProps, props)}
                  section={section}
                  subsections={subsections}
                />
              </section>
            );
          }
        )}
    </>
  );
};

export { DetailMainTab };
