import React, { useEffect, useRef, useState } from "react";
import { i18next } from "@translations/invenio_app_rdm/i18next";
import { Placeholder } from "semantic-ui-react";
import { FileListBox, EmbargoMessage } from "./FileList";

const FilePreview = ({
  activePreviewFile,
  defaultPreviewFile,
  files,
  hasFiles,
  hasPreviewableFiles,
  isPreview,
  permissions,
  previewFileUrl,
  record,
  setActivePreviewFile,
  totalFileSize,
  useDynamicPreview = true,
}) => {
  const [loading, setLoading] = useState(true);
  console.log("****FilePreview loading", loading);
  const previewUrlFlag = isPreview ? "&preview=1" : "";
  const fileToShow = useDynamicPreview ? activePreviewFile : defaultPreviewFile;

  const iFrameRef = useRef(null);
  const iframeCurrent = iFrameRef.current;
  console.log("****FilePreview iFrameRef", iFrameRef);
  console.log("****FilePreview iframeCurrent", iframeCurrent);
  useEffect(() => {
    console.log("****FilePreview iFrameRef", iFrameRef);
    console.log("****FilePreview iframeCurrent", iframeCurrent);
    iFrameRef.current?.addEventListener("load", () => setLoading(false));
    return () => {
      iFrameRef.current?.removeEventListener("load", () => setLoading(false));
    };
  }, [iFrameRef.current]);

  return (
    !!hasFiles && (
      <section id="record-file-preview" aria-label={i18next.t("File preview")}>
        {permissions.can_read_files && hasPreviewableFiles && (
          <>
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
            {!!loading && (
              <>
                <div className="placeholder-header-bar" />
                <Placeholder fluid>
                  {[...Array(8).keys()].map((e) => (
                    <Placeholder.Paragraph>
                      {[...Array(8).keys()].map((e) => (
                        <Placeholder.Line key={e} />
                      ))}
                      <Placeholder.Line />
                    </Placeholder.Paragraph>
                  ))}
                </Placeholder>
              </>
            )}
            <iframe
              title={i18next.t("Preview")}
              className={`preview-iframe ${loading ? "hidden" : ""}`}
              id={record.id}
              ref={iFrameRef}
              name={record.id}
              src={`${previewFileUrl}${fileToShow.key}?${previewUrlFlag}`}
              width="100%"
              // height="800"
            ></iframe>
          </>
        )}

        {/* {permissions.can_read_files && !hasPreviewableFiles && ( */}
        {/* {permissions.can_read_files && hasPreviewableFiles && (
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
        )} */}

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
