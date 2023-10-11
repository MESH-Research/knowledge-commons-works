import React from "react";
import { Descriptions } from "../components/Descriptions";
import { FilePreview } from "../components/FilePreview";

const contentComponents = {
  'descriptions': {"component": Descriptions,
                   "passed_args": ["description",
                                   "additional_descriptions", "has_files"],
                  },
  'preview': {"component": FilePreview,
              "passed_args": ["files", "isPreview",
                              "hasPreviewableFiles", "permissions",
                              "previewFile", "previewFileUrl", "record", "totalFileSize"],
              "show_if_true": ({has_files}) => !!has_files
             },
}

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
const DetailMainTab = (props) => {
  console.log('@@@@@props', props);
  return (
    <>
      {!!props.subSections.length && props.subSections.map((section, idx) => {

        const SubSectionComponent = contentComponents[section]['component'];
        const subSectionArgs = contentComponents[section]['passed_args'].reduce((obj, key) => { obj[key] = props[key]; return obj }, {});
        console.log('****subSectionArgs', subSectionArgs);
        const showIfTrue = !!showIfTrue ? contentComponents[section]['show_if_true'] : () => true;

        return showIfTrue(subSectionArgs) ? (
          <SubSectionComponent {...subSectionArgs} key={idx} /> ) : "";
        }
      )}
    </>
  )
};

export { DetailMainTab };