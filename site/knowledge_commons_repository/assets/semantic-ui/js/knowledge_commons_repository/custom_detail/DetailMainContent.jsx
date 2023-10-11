import React, { useState } from "react";
import { i18next } from '@translations/invenio_app_rdm/i18next';
import {
  Button,
  Tab
} from 'semantic-ui-react'
import Creatibutors from "./components/Creatibutors";

const RecordTitle = ({title}) => {
    return (
      <section
        id="record-title-section"
        aria-label={i18next.t('Record title and creators')}
      >
        <h1 id="record-title"
          className="wrap-overflowing-text"
        >
          {title}
        </h1>
      </section>
    );
};

const Descriptions = ({description, additional_descriptions}) => {
  const [ open, setOpen ] = useState(false);
  return (
    <>
    {description && (
      <section id="description"
        className="rel-mt-2"
        aria-label={i18next.t('Record description')}
      >
        <h2 id="description-heading">{i18next.t('Description')}</h2>
        {(description.length > 240) ? (
          <>
          <p>{open ? description : `${description.substring(0, 240)}...`}</p>
          <Button onClick={() => setOpen(!open)}>{open ? 'Show less' : 'Show more'}</Button>
          </>
        ) : <p>{description}</p>}
      </section>
    )}
    {additional_descriptions && open && (
      additional_descriptions.map((add_description, idx) => (
        <section id={`additional-description-${idx}`}
          key={`additional-description-${idx}`}
          className="rel-mt-2"
          aria-label={i18next.t(add_description.type.title_l10n)}
        >
          <h2>{i18next.t(add_description.type.title_l10n)}
            <span className="text-muted language">
              {add_description.lang ? `(${add_description.lang.title_l10n})` : ""}
            </span>
          </h2>
          <p>{add_description.description}</p>
        </section>
      ))
    )}
    </>
  );
};

const EmbargoMessage = ({record}) => {
  return (
    <div class={`ui ${record.ui.access_status.message_class} message file-box-message`}
    >
      <i class={`ui ${record.ui.access_status.icon} icon`}></i>
      <b>{record.ui.access_status.title_l10n}</b>
      <p>{record.ui.access_status.description_l10n}</p>
      {!!record.access.embargo.reason ? (
        <p>{i18next.t("Reason")}: {record.access.embargo.reason}</p>
      ) : ""}
    </div>
  )
};

const FileListTableRow = ({file,
                           downloadFileUrl,
                           pid,
                           isPreview,
                           record,
                           withPreview=true}) => {
  const file_type = file.key.split('.').pop().toLowerCase();
  const previewUrlFlag = isPreview ? "&preview=1" : "";
  const downloadUrl = `${downloadFileUrl.replace('/preview/', '/files/')}/${file.key}?download=1${previewUrlFlag}`;
  const previewUrl = `${downloadFileUrl}/${file.key}?${previewUrlFlag}`;
  return (
      <tr>
        <td class="ten wide" >
          <div>
            <a href={downloadUrl}>{file.key}</a>
          </div>
          <small class="ui text-muted font-tiny">{file.checksum}
          <div class="ui icon inline-block" data-tooltip={i18next.t('This is the file fingerprint (checksum), which can be used to verify the file integrity.')}>
            <i class="question circle checksum icon"></i>
          </div>
          </small>
        </td>
        <td>{file.size}</td>
        <td class="right aligned">
          <span>
            {/* FIXME: restrict to previewable file types */}
            { withPreview && (
              <a role="button" class="ui compact mini button preview-link" href={previewUrl} target="preview-iframe" data-file-key={file.key}>
                <i class="eye icon"></i> {i18next.t("Preview")}
              </a>
            )}
            <a role="button" class="ui compact mini button" href={downloadUrl}>
              <i class="download icon"></i>
              {i18next.t('Download')}
            </a>
          </span>
        </td>
      </tr>
  )
};


const FileListTable = ({downloadFileUrl,
                        files,
                        pid,
                        isPreview,
                        record,
                        withPreview=true
                        }) => {
  return (
    <table class="ui striped table files fluid">
      <thead>
        <tr>
          <th>{i18next.t('Name')}</th>
          <th>{i18next.t('Size')}</th>
          <th class>
            <a role="button" class="ui compact mini button right floated archive-link" href={record.links.archive}>
              <i class="file archive icon button"></i> {i18next.t("Download all")}
            </a>
          </th>
        </tr>
      </thead>
      <tbody>
      {files.map(
        (file) => (
          <FileListTableRow
            downloadFileUrl={downloadFileUrl}
            file={file}
            pid={pid}
            isPreview={isPreview}
            record={record}
            withPreview={withPreview}
          />
          )
      )}
      </tbody>
    </table>
  )
};

const FileListBox = ({downloadFileUrl,
                      files,
                      isPreview,
                      recordId,
                      record,
                      totalFileSize}) => {
  return (
    <div class="">
      <div class="ui accordion panel mb-10 {{record.ui.access_status.id}}" id="preview" href="#collapsablePreview">
        <div class="active title trigger panel-heading {{record.ui.access_status.id}}" tabIndex="0">
          {i18next.t("Files")}
          <small class="text-muted">{totalFileSize}</small>
          <i class="angle right icon"></i>
        </div>
        <div class="active content pt-0">
          {record.access.files == 'restricted' ? (
            <EmbargoMessage record={record} />
          )
          : (
            <FileListTable
              downloadFileUrl={downloadFileUrl}
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

const FilePreview = ({downloadFileUrl,
                      files,
                      hasPreviewableFiles,
                      isPreview,
                      permissions,
                      previewFile,
                      record,
                      totalFileSize}) => {

  // let ordered_entries = files.entries;
  // if (files.enabled && files.order.length > 0) {
  //   ordered_entries = files.order.map((file_key) => files.entries[file_key]);
  // }
  // let previewable_entries = [];
  // if ( ordered_entries.length > 0 ) {
  //   previewable_entries = ordered_entries.filter((file) => {
  //     const ext = file.key.split('.').pop().toLowerCase();
  //     // FIXME: get this list from the backend invenio-previewer or
  //     // invenio-app-rdm has_previewable_files func
  //     return ['txt', 'pdf', 'epub', 'html', 'doc', 'docx', 'jpg',
  //             'jpeg', 'png', 'ppt'].includes(ext);
  //   });
  // }

  const previewUrlFlag = isPreview ? "&preview=1" : "";
  const previewUrl = `${downloadFileUrl}/${previewFile.key}?${previewUrlFlag}`;
  console.log("****previewUrl", previewUrl);
  console.log("****previewFile", previewFile);
  console.log("****downloadFileUrl", downloadFileUrl);

  return (
    <section id="record-files" className="rel-mt-2"
      aria-label={i18next.t('Files')}
    >
      {permissions.can_read_files && hasPreviewableFiles && (
        <div className="">
          <div className={`ui accordion panel mb-10 ${record.ui.access_status.id}`}
            id="preview"
            href="#collapsablePreview"
          >
            <div className={`active title trigger panel-heading ${record.ui.access_status.id} truncated`}
              tabIndex="0"
              aria-label={i18next.t('File preview')}
            >
              <span id="preview-file-title">{previewFile.key}</span>
              <i className="ui angle right icon"></i>
            </div>
            <div id="collapsablePreview" className="active content pt-0">
              <div>
                <iframe
                  title={i18next.t('Preview')}
                  className="preview-iframe"
                  id={record.id}
                  name={record.id}
                  width="100%"
                  height="800"
                  src={previewUrl}
                >
                </iframe>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* {permissions.can_read_files && !hasPreviewableFiles && ( */}
      {permissions.can_read_files && hasPreviewableFiles && (
        <>
        <h2 id="files-heading">{i18next.t('Files')}</h2>
        <FileListBox
          downloadFileUrl={downloadFileUrl}
          files={files}
          recordId={record.id}
          isPreview={isPreview}
          record={record}
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
            <div className="active title trigger panel-heading {{ record.ui.access_status.id }}"
            >
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
  );
}

const Content = ({additional_descriptions,
                  description,
                  downloadFileUrl,
                  files,
                  hasPreviewableFiles,
                  isPreview,
                  permissions,
                  previewFile,
                  record,
                  totalFileSize
                }) => {
  return (
    <>
      <Descriptions description={description}
                    additional_descriptions={additional_descriptions}
                    has_files={record.files.enabled}
      />
      {record.files.enabled ? (
        <FilePreview
          downloadFileUrl={downloadFileUrl}
          files={files}
          isPreview={isPreview}
          hasPreviewableFiles={hasPreviewableFiles}
          permissions={permissions}
          previewFile={previewFile}
          record={record}
          totalFileSize={totalFileSize}
        />
      ) : ""}
    </>
  )
};

const DetailMainContent = ({community,
                            customFieldsUi,
                            externalResources,
                            downloadFileUrl,
                            files,
                            hasPreviewableFiles,
                            iconsRor,
                            iconsGnd,
                            iconsHcUsername,
                            iconsOrcid,
                            isDraft,
                            isPreview,
                            landingUrls,
                            record,
                            permissions,
                            previewFile,
                            totalFileSize
                          }) => {
    const panes = [
      { menuItem: 'Content', render: () => (
        <Tab.Pane>
          <Content
            additional_descriptions={record.ui.additional_descriptions ? record.ui.additional_descriptions : null}
            description={record.metadata.description}
            downloadFileUrl={downloadFileUrl}
            files={files}
            hasPreviewableFiles={hasPreviewableFiles}
            isPreview={isPreview}
            permissions={permissions}
            previewFile={previewFile}
            record={record}
            totalFileSize={totalFileSize}
          />
        </Tab.Pane>)},
      { menuItem: 'Details', render: () => <Tab.Pane>Tab 2 Content</Tab.Pane> },
      { menuItem: 'Authors', render: () => <Tab.Pane>Tab 3 Content</Tab.Pane> },
      { menuItem: 'Subjects', render: () => <Tab.Pane>Tab 3 Content</Tab.Pane> },
      { menuItem: 'Funders', render: () => <Tab.Pane>Tab 3 Content</Tab.Pane> },
      { menuItem: 'Citation', render: () => <Tab.Pane>Tab 3 Content</Tab.Pane> },
      { menuItem: 'Analytics', render: () => <Tab.Pane>Tab 3 Content</Tab.Pane> },
    ]
    return (
      <>
        <RecordTitle title={record.metadata.title} />
        <Creatibutors
          creators={record.ui.creators}
          contributors={record.ui.contributors}
          iconsRor={iconsRor}
          iconsGnd={iconsGnd}
          iconsHcUsername={iconsHcUsername}
          iconsOrcid={iconsOrcid}
          landingUrls={landingUrls}
        />
        <article className="sixteen wide tablet eleven wide computer column main-record-content">
          <Tab panes={panes} />
        </article>
      </>
    );
};

export default DetailMainContent;