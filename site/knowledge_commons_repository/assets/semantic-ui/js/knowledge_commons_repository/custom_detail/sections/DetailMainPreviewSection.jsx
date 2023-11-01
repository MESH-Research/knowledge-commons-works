import React from "react";
import { FilePreview } from "../components/FilePreview";

function FilePreviewWrapper({
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
}) {
  return (
    <FilePreview
      activePreviewFile={activePreviewFile}
      previewFileUrl={previewFileUrl}
      files={files}
      hasFiles={hasFiles}
      hasPreviewableFiles={hasPreviewableFiles}
      isPreview={isPreview}
      permissions={permissions}
      defaultPreviewFile={defaultPreviewFile}
      record={record}
      setActivePreviewFile={setActivePreviewFile}
      totalFileSize={totalFileSize}
      useDynamicPreview={false}
    />
  );
}

export { FilePreviewWrapper };
