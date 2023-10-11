import React from 'react';
import { i18next } from '@translations/invenio_app_rdm/i18next';

const EmbargoMessage = ({record}) => {
  return (
    <div className={`ui ${record.ui.access_status.message_class} message file-box-message`}
    >
      <i className={`ui ${record.ui.access_status.icon} icon`}></i>
      <b>{record.ui.access_status.title_l10n}</b>
      <p>{record.ui.access_status.description_l10n}</p>
      {!!record.access.embargo.reason ? (
        <p>{i18next.t("Reason")}: {record.access.embargo.reason}</p>
      ) : ""}
    </div>
  )
};

const FileListTableRow = ({file,
                           previewFileUrl,
                           isPreview,
                           withPreview=true}) => {
  const file_type = file.key.split('.').pop().toLowerCase();
  const previewUrlFlag = isPreview ? "&preview=1" : "";
  const downloadUrl = `${previewFileUrl.replace('/preview/', '/files/')}/${file.key}?download=1${previewUrlFlag}`;
  const previewUrl = `${previewFileUrl}/${file.key}?${previewUrlFlag}`;
  return (
      <tr>
        <td className="ten wide" >
          <div>
            <a href={downloadUrl}>{file.key}</a>
          </div>
          <small className="ui text-muted font-tiny">{file.checksum}
          <div className="ui icon inline-block" data-tooltip={i18next.t('This is the file fingerprint (checksum), which can be used to verify the file integrity.')}>
            <i className="question circle checksum icon"></i>
          </div>
          </small>
        </td>
        <td>{file.size}</td>
        <td className="right aligned">
          <span>
            {/* FIXME: restrict to previewable file types */}
            { withPreview && (
              <a role="button" className="ui compact mini button preview-link" href={previewUrl} target="preview-iframe" data-file-key={file.key}>
                <i className="eye icon"></i> {i18next.t("Preview")}
              </a>
            )}
            <a role="button" className="ui compact mini button" href={downloadUrl}>
              <i className="download icon"></i>
              {i18next.t('Download')}
            </a>
          </span>
        </td>
      </tr>
  )
};


const FileListTable = ({previewFileUrl,
                        files,
                        pid,
                        isPreview,
                        record,
                        withPreview=true
                        }) => {
  return (
    <table className="ui striped table files fluid">
      <thead>
        <tr>
          <th>{i18next.t('Name')}</th>
          <th>{i18next.t('Size')}</th>
          <th class>
            <a role="button" className="ui compact mini button right floated archive-link" href={record.links.archive}>
              <i className="file archive icon button"></i> {i18next.t("Download all")}
            </a>
          </th>
        </tr>
      </thead>
      <tbody>
      {files.map(
        (file) => (
          <FileListTableRow
            key={file.key}
            previewFileUrl={previewFileUrl}
            file={file}
            isPreview={isPreview}
            withPreview={withPreview}
          />
          )
      )}
      </tbody>
    </table>
  )
};

const FileListBox = ({previewFileUrl,
                      files,
                      isPreview,
                      recordId,
                      record,
                      totalFileSize}) => {
  return (
    <div className="">
      <div className="ui accordion panel mb-10 {{record.ui.access_status.id}}" id="preview" href="#collapsablePreview">
        <div className="active title trigger panel-heading {{record.ui.access_status.id}}" tabIndex="0">
          {i18next.t("Files")}
          <small className="text-muted">{totalFileSize}</small>
          <i className="angle right icon"></i>
        </div>
        <div className="active content pt-0">
          {record.access.files == 'restricted' ? (
            <EmbargoMessage record={record} />
          )
          : (
            <FileListTable
              previewFileUrl={previewFileUrl}
              files={files}
              pid={recordId}
              isPreview={isPreview}
              record={record}
              withPreview={true}
            />
          )
        }
          <div id="collapsableFiles">
          </div>
        </div>
      </div>
    </div>
  )
};

export {
    FileListBox,
    FileListTable,
    FileListTableRow,
    EmbargoMessage
}