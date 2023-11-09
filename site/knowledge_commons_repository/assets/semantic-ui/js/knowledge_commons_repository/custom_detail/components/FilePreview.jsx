import React, { useEffect, useRef, useState } from "react";
import { i18next } from "@translations/invenio_app_rdm/i18next";
import { Placeholder } from "semantic-ui-react";
import { EmbargoMessage } from "./EmbargoMessage";

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
  const fileExtension = fileToShow?.key?.split(".").pop();

  const iFrameRef = useRef(null);
  const iframeCurrent = iFrameRef.current;
  useEffect(() => {
    iFrameRef.current?.addEventListener("load", () => setLoading(false));
    return () => {
      iFrameRef.current?.removeEventListener("load", () => setLoading(false));
    };
  }, [iFrameRef.current]);

  return (
    <>
      {record.access.files === "restricted" && (
        <EmbargoMessage record={record} />
      )}
      {!!hasFiles && permissions.can_read_files && (
        <section
          id="record-file-preview"
          aria-label={i18next.t("File preview")}
        >
          {!!hasPreviewableFiles && (
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
                className={`preview-iframe ${
                  loading ? "hidden" : ""
                } ${fileExtension}`}
                id={record.id}
                ref={iFrameRef}
                name={record.id}
                src={`${previewFileUrl}${fileToShow.key}?${previewUrlFlag}`}
                width="100%"
                // height="800"
              ></iframe>
            </>
          )}
        </section>
      )}
    </>
  );
};

export { FilePreview };
