import React from "react";
import { i18next } from "@translations/invenio_app_rdm/i18next";
import { Button, Icon } from "semantic-ui-react";
import { FileListDropdown } from "../components/FileList";

const SidebarDownloadSection = ({
  defaultPreviewFile,
  files,
  fileTabIndex,
  hasFiles,
  isPreview,
  permissions,
  previewFileUrl,
  previewTabIndex,
  record,
  setActiveTab,
  show,
  show_heading,
  totalFileSize,
}) => {
  const previewUrlFlag = isPreview ? "&preview=1" : "";
  console.log("****SidebarDownloadSection files", files);
  return (
    hasFiles && (
      <div
        id="download"
        className={`sidebar-container ${show}`}
        aria-label={i18next.t("File download")}
      >
        {show_heading === true && (
          <h2 className="ui medium top attached header mt-0">
            {i18next.t("Download")}
          </h2>
        )}
        <FileListDropdown
          id="record-details-download"
          defaultPreviewFile={defaultPreviewFile}
          files={files}
          fileCountToShow={3}
          fileTabIndex={fileTabIndex}
          fullWordButtons={false}
          withPreview={false}
          isPreview={isPreview}
          permissions={permissions}
          previewFileUrl={previewFileUrl}
          previewTabIndex={previewTabIndex}
          record={record}
          setActiveTab={setActiveTab}
          showChecksum={false}
          showHeading={show_heading}
          showTableHeader={false}
          showTotalSize={false}
          stackedRows={true}
          totalFileSize={totalFileSize}
        />
      </div>
    )
  );
};

export { SidebarDownloadSection };
