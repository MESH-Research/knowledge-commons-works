import React from 'react';
import { i18next } from '@translations/invenio_app_rdm/i18next';
import { FileListBox, EmbargoMessage } from './FileList';

const FilePreview = ({previewFileUrl,
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
  console.log('++++previewFile', previewFile);
  const previewUrl = `${previewFileUrl}/${previewFile.key}?${previewUrlFlag}`;

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
          previewFileUrl={previewFileUrl}
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

export {
    FilePreview
}