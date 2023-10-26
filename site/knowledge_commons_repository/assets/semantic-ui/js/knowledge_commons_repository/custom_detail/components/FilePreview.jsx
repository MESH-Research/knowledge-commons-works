import React, { useState } from "react";
import { i18next } from "@translations/invenio_app_rdm/i18next";
import { FileListBox, EmbargoMessage } from "./FileList";

const FilePreview = ({
  activePreviewFile,
  previewFileUrl,
  files,
  hasFiles,
  hasPreviewableFiles,
  isPreview,
  permissions,
  defaultPreviewFile,
  record,
  setActivePreviewFile,
  totalFileSize,
}) => {
  const previewUrlFlag = isPreview ? "&preview=1" : "";
  console.log("****FilePreview previewFile", defaultPreviewFile);
  console.log("****FilePreview activePreviewFile", activePreviewFile);

  return (
    !!hasFiles && (
      <section
        id="record-files"
        className="rel-mt-2"
        aria-label={i18next.t("Files")}
      >
        {permissions.can_read_files && hasPreviewableFiles && (
          <div className="">
            {/* <div
              className={`ui accordion panel mb-10 ${record.ui.access_status.id}`}
              id="preview"
              href="#collapsablePreview"
            >
              <div
                className={`active title trigger panel-heading ${record.ui.access_status.id} truncated`}
                tabIndex="0"
                aria-label={i18next.t("File preview")}
              >
                <span id="preview-file-title">{activePreviewFile.key}</span>
                <i className="ui angle right icon"></i>
              </div> */}
            <div id="collapsablePreview" className="active content pt-0">
              <div>
                <iframe
                  title={i18next.t("Preview")}
                  className="preview-iframe"
                  id={record.id}
                  name={record.id}
                  width="100%"
                  height="800"
                  src={`${previewFileUrl}${activePreviewFile.key}?${previewUrlFlag}`}
                ></iframe>
              </div>
            </div>
            {/* </div> */}
          </div>
        )}

        {/* {permissions.can_read_files && !hasPreviewableFiles && ( */}
        {permissions.can_read_files && hasPreviewableFiles && (
          <>
            <h2 id="files-heading">{i18next.t("Files")}</h2>
            <FileListBox
              activePreviewFile={activePreviewFile}
              files={files}
              recordId={record.id}
              isPreview={isPreview}
              previewFileUrl={previewFileUrl}
              record={record}
              setActivePreviewFile={setActivePreviewFile}
              totalFileSize={totalFileSize}
            />
          </>
        )}

        {!permissions.can_read_files && (
          <div className="pt-0 pb-20">
            <div
              className={`ui accordion panel mb-10 ${record.ui.access_status.id}`}
              id="preview"
              href="#collapsablePreview"
            >
              <div className="active title trigger panel-heading {{ record.ui.access_status.id }}">
                {i18next.t("Files")}
                <i class="angle down icon"></i>
              </div>
              <div id="collapsablePreview" className="active content pt-0">
                <EmbargoMessage record={record} />
              </div>
            </div>
          </div>
        )}
      </section>
    )
  );
};

export { FilePreview };
