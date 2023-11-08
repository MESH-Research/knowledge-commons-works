import React from "react";
import { i18next } from "@translations/invenio_app_rdm/i18next";
import { Button, Dropdown, Icon } from "semantic-ui-react";
import { formatBytes, getFileTypeIconName } from "../util";
import { EmbargoMessage } from "./EmbargoMessage";

const FileListTableRow = ({
  file,
  fileTabIndex,
  fullWordButtons,
  isPreview,
  previewFileUrl,
  previewTabIndex,
  setActivePreviewFile,
  setActiveTab,
  showChecksum,
  stackedRows,
  withPreview,
}) => {
  // FIXME: restrict to previewable file types
  const file_type = file.key.split(".").pop().toLowerCase();
  const previewUrlFlag = isPreview ? "&preview=1" : "";
  const downloadUrl = `${previewFileUrl.replace("/preview/", "/files/")}/${
    file.key
  }?download=1${previewUrlFlag}`;

  const handlePreviewChange = (file) => {
    // this was originally used when files list was on a different tab
    // from the preview box
    // setActiveTab(previewTabIndex);
    setActivePreviewFile(file);
  };

  return (
    <tr>
      <td className={`${!!stackedRows ? "fourteen" : "nine"} wide`}>
        <div>
          <a href={downloadUrl} className="filename">
            {file.key}
          </a>
        </div>
        {!!stackedRows && (
          <small className="ui text-muted">{formatBytes(file.size)}</small>
        )}
        {!!showChecksum && (
          <small className="ui text-muted font-tiny">
            {file.checksum}
            <div
              className="ui icon inline-block"
              data-tooltip={i18next.t(
                "This is the file fingerprint (checksum), which can be used to verify the file integrity."
              )}
            >
              <i className="question circle checksum icon"></i>
            </div>
          </small>
        )}
      </td>
      {!stackedRows && <td>{formatBytes(file.size)}</td>}
      <td className="right aligned">
        <span>
          {/* FIXME: restrict to previewable file types */}
          {withPreview && (
            <Button
              role="button"
              className="ui compact mini button preview-link"
              target="preview-iframe"
              data-file-key={file.key}
              size="mini"
              onClick={() => handlePreviewChange(file)}
              compact
            >
              <i className="eye icon"></i> {i18next.t("Preview")}
            </Button>
          )}
          <a
            role="button"
            className="ui compact mini button"
            href={downloadUrl}
          >
            <i className="download icon"></i>
            {!!fullWordButtons && i18next.t("Download")}
          </a>
        </span>
      </td>
    </tr>
  );
};

const FileListTable = ({
  activePreviewFile,
  fileCountToShow,
  files,
  fileTabIndex,
  fullWordButtons,
  isPreview,
  previewFileUrl,
  previewTabIndex,
  record,
  setActivePreviewFile,
  setActiveTab,
  showChecksum,
  showTableHeader,
  showTotalSize,
  stackedRows,
  totalFileSize,
  withPreview,
}) => {
  const displayFiles =
    fileCountToShow > 0 ? files.slice(0, fileCountToShow) : files;
  return (
    <>
      <table className="ui striped table files fluid">
        {!!showTableHeader && (
          <thead>
            <tr>
              <th>{i18next.t("Name")}</th>
              <th>{i18next.t("Size")}</th>
              <th></th>
            </tr>
          </thead>
        )}
        <tbody>
          {!!showTotalSize && (
            <tr className={`title ${record.ui.access_status.id}`} tabIndex="0">
              <td>{i18next.t(`All ${files.length} files (as zip archive)`)}</td>
              <td>{totalFileSize} in total</td>
              <td>
                <a
                  role="button"
                  className="ui compact mini button right floated archive-link"
                  href={record.links.archive}
                >
                  <i className="file archive icon button"></i>{" "}
                  {i18next.t("Download all")}
                </a>
              </td>
            </tr>
          )}
          {displayFiles.map((file) => (
            <FileListTableRow
              activePreviewFile={activePreviewFile}
              key={file.key}
              file={file}
              fileTabIndex={fileTabIndex}
              fullWordButtons={fullWordButtons}
              isPreview={isPreview}
              previewFileUrl={previewFileUrl}
              previewTabIndex={previewTabIndex}
              setActivePreviewFile={setActivePreviewFile}
              setActiveTab={setActiveTab}
              showChecksum={showChecksum}
              stackedRows={stackedRows}
              withPreview={withPreview}
            />
          ))}
        </tbody>
      </table>
      {fileCountToShow > 0 && fileCountToShow < files.length && (
        <Button
          role="button"
          floated="right"
          size="mini"
          className="ui compact archive-link"
          aria-label="See more files"
          compact
          onClick={() => setActiveTab(fileTabIndex)}
        >
          <i className="file archive icon button"></i>{" "}
          {i18next.t("See more files")}
        </Button>
      )}
    </>
  );
};

const FileListDropdown = ({
  defaultPreviewFile,
  fileCountToShow,
  files,
  fileTabIndex,
  isPreview,
  permissions,
  previewFileUrl,
  record,
  setActiveTab,
  totalFileSize,
}) => {
  const previewUrlFlag = isPreview ? "&preview=1" : "";
  return (
    <>
      {/* access is "restricted" also if record is metadata-only */}
      {record.access.files === "restricted" && (
        <EmbargoMessage record={record} />
      )}
      {!!permissions.can_read_files &&
        (files?.length < 2 ? (
          <Button
            id="record-details-download"
            positive
            fluid
            as="a"
            href={`${previewFileUrl.replace("/preview/", "/files/")}/${
              defaultPreviewFile.key
            }?download=1${previewUrlFlag}`}
            content={i18next.t("Download")}
            icon="download"
            labelPosition="right"
          ></Button>
        ) : (
          <Dropdown
            text="Download"
            icon="download"
            button
            labeled
            fluid
            className="icon positive right labeled"
          >
            <Dropdown.Menu>
              {/* <Dropdown.Header>Choose a file</Dropdown.Header> */}
              {files.map(({ key, size }) => (
                <Dropdown.Item
                  href={`${previewFileUrl.replace(
                    "/preview/",
                    "/files/"
                  )}/${key}?download=1${previewUrlFlag}`}
                >
                  <span className="text">{key}</span>
                  <small className="description filesize">
                    <Icon name={getFileTypeIconName(key)} />
                    {formatBytes(size)}
                  </small>
                </Dropdown.Item>
              ))}
              <Dropdown.Divider />
              <Dropdown.Item
                href={record.links.archive}
                icon={"archive"}
                text={i18next.t(`Download all`)}
                description={totalFileSize}
              ></Dropdown.Item>
              <Dropdown.Divider />
              <Dropdown.Item
                text="File details and previews"
                icon={"eye"}
                onClick={() => setActiveTab(fileTabIndex)}
              ></Dropdown.Item>
            </Dropdown.Menu>
          </Dropdown>
        ))}
    </>
  );
};

const FileListBox = ({
  activePreviewFile,
  fileCountToShow = 0,
  files,
  fileTabIndex,
  fullWordButtons = true,
  isPreview,
  permissions,
  previewFileUrl,
  previewTabIndex,
  record,
  setActiveTab,
  setActivePreviewFile,
  showChecksum = true,
  showEmbargoMessage = false,
  showTableHeader = true,
  showTotalSize = true,
  stackedRows = false,
  totalFileSize,
  withPreview,
}) => {
  return (
    <div className={`ui mb-10 ${record.ui.access_status.id}`}>
      <div className="content pt-0">
        {/* Note: "restricted" is the value also for metadata-only records */}
        {record.access.files === "restricted" && showEmbargoMessage && (
          <EmbargoMessage record={record} />
        )}
        {!!permissions.can_read_files && (
          <FileListTable
            activePreviewFile={activePreviewFile}
            previewFileUrl={previewFileUrl}
            files={files}
            fileCountToShow={fileCountToShow}
            fileTabIndex={fileTabIndex}
            fullWordButtons={fullWordButtons}
            pid={record.id}
            isPreview={isPreview}
            permissions={permissions}
            previewTabIndex={previewTabIndex}
            record={record}
            setActivePreviewFile={setActivePreviewFile}
            setActiveTab={setActiveTab}
            showChecksum={showChecksum}
            showTableHeader={showTableHeader}
            showTotalSize={showTotalSize}
            stackedRows={stackedRows}
            totalFileSize={totalFileSize}
            withPreview={withPreview !== undefined ? withPreview : true}
          />
        )}
      </div>
    </div>
  );
};

export {
  FileListBox,
  FileListDropdown,
  FileListTable,
  FileListTableRow,
  EmbargoMessage,
};
