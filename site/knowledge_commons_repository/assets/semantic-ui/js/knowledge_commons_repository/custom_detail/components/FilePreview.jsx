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
  const previewUrlFlag = isPreview ? "&preview=1" : "";
  const fileToShow = useDynamicPreview ? activePreviewFile : defaultPreviewFile;

  const iFrameRef = useRef(null);
  const iframeCurrent = iFrameRef.current;
  useEffect(() => {
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
