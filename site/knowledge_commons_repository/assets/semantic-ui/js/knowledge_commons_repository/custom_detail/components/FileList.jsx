import React from "react";
import { i18next } from "@translations/invenio_app_rdm/i18next";
import { Button, Dropdown, Icon, Menu } from "semantic-ui-react";
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
      <td
        className={`${!!stackedRows ? "fourteen" : "nine"} wide ${
          !!showChecksum && "with-checksum"
        }`}
      >
        <span className="mobile only download-button-wrapper">
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
              <i className="eye icon"></i>
              <span className="tablet computer only">
                {" "}
                {i18next.t("Preview")}
              </span>
            </Button>
          )}
          <Button
            role="button"
            className="ui compact mini button"
            href={downloadUrl}
          >
            <i className="download icon"></i>
            <span className="tablet computer only">
              {!!fullWordButtons && i18next.t("Download")}
            </span>
          </Button>
        </span>
        <div>
          <a href={downloadUrl} className="filename">
            {file.key}
          </a>
        </div>
        <small
          className={`ui text-muted ${
            !stackedRows ? "mobile only" : ""
          } filesize`}
        >
          {formatBytes(file.size)}
        </small>{" "}
        {!!showChecksum && (
          <small className="ui text-muted font-tiny checksum">
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
      <td
        className={`single line ${!stackedRows ? "tablet computer only" : ""}`}
      >
        {formatBytes(file.size)}
      </td>
      <td className="right aligned collapsing tablet computer only">
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
              <i className="eye icon"></i>
              <span className="tablet computer only">
                {" "}
                {i18next.t("Preview")}
              </span>
            </Button>
          )}
          <a
            role="button"
            className="ui compact mini button"
            href={downloadUrl}
          >
            <i className="download icon"></i>
            <span className="tablet computer only">
              {!!fullWordButtons && i18next.t("Download")}
            </span>
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
      <table className="ui striped table files fluid unstackable">
        {!!showTableHeader && (
          <thead>
            <tr>
              <th>{i18next.t("Name")}</th>
              <th className="computer tablet only">{i18next.t("Size")}</th>
              <th className="computer tablet only"></th>
            </tr>
          </thead>
        )}
        <tbody>
          {!!showTotalSize && files.length > 1 && (
            <tr
              className={`title ${record.ui.access_status.id} total-files`}
              tabIndex="0"
            >
              <td>
                {i18next.t(`All ${files.length} files (as zip archive)`)}
                <a
                  role="button"
                  className="ui compact mini button right floated archive-link mobile only"
                  href={record.links.archive}
                >
                  <i className="file archive icon button"></i>
                  <span className="tablet computer only">
                    {" "}
                    {i18next.t("Download all")}
                  </span>
                </a>
              </td>
              <td className="tablet computer only">{totalFileSize} in total</td>
              <td className="tablet computer only">
                <a
                  role="button"
                  className="ui compact mini button right floated archive-link"
                  href={record.links.archive}
                >
                  <i className="file archive icon button"></i>
                  <span className="tablet computer only">
                    {" "}
                    {i18next.t("Download all")}
                  </span>
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

const FileListDropdownMenu = ({
  asButton = true,
  asLabeled = true,
  asFluid = true,
  asItem = false,
  classNames = "icon positive right labeled",
  files,
  fileTabIndex,
  icon = "download",
  id,
  previewFileUrl,
  previewUrlFlag,
  record,
  setActiveTab,
  text = "Download",
  totalFileSize,
}) => {
  return (
    <Dropdown
      id={id}
      text={text}
      button={asButton}
      icon={icon}
      labeled={asLabeled}
      fluid={asFluid}
      className={classNames}
      item={asItem}
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
  );
};

const FileListItemDropdown = ({
  defaultPreviewFile,
  fileCountToShow,
  files,
  fileTabIndex,
  handleMobileMenuClick,
  id,
  isPreview,
  permissions,
  previewFileUrl,
  record,
  setActiveTab,
  showEmbargoMessage,
  totalFileSize,
}) => {
  const previewUrlFlag = isPreview ? "&preview=1" : "";
  return (
    <>
      {/* access is "restricted" also if record is metadata-only */}
      {!!permissions.can_read_files &&
        (files?.length < 2 ? (
          <Menu.Item
            id={id}
            as="a"
            href={`${previewFileUrl.replace("/preview/", "/files/")}/${
              defaultPreviewFile.key
            }?download=1${previewUrlFlag}`}
            name="download"
            // active={activeItem === "video play"}
            onClick={handleMobileMenuClick}
          >
            <Icon name="download" />
            Download
          </Menu.Item>
        ) : (
          <FileListDropdownMenu
            {...{
              icon: false,
              files,
              fileTabIndex,
              id,
              record,
              previewFileUrl,
              previewUrlFlag,
              setActiveTab,
              text: (
                <>
                  <Icon name="download" />
                  Download
                </>
              ),
              totalFileSize,
              asButton: false,
              asLabeled: false,
              asFluid: false,
              asItem: true,
              classNames: "pointing",
            }}
          />
        ))}
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
  showEmbargoMessage,
  totalFileSize,
}) => {
  const previewUrlFlag = isPreview ? "&preview=1" : "";
  return (
    <>
      {/* access is "restricted" also if record is metadata-only */}
      {record.access.files === "restricted" && showEmbargoMessage === true && (
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
          <FileListDropdownMenu
            {...{
              files,
              fileTabIndex,
              previewFileUrl,
              previewUrlFlag,
              record,
              setActiveTab,
              totalFileSize,
            }}
          />
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
  FileListItemDropdown,
  FileListTable,
  FileListTableRow,
  EmbargoMessage,
};
