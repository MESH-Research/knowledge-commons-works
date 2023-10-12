import React from 'react';
import { i18next } from '@translations/invenio_app_rdm/i18next';
import { RecordVersionsList } from '../components/RecordVersionList';

const VersionsSection = ({isPreview,
                          record
                        }) => {
  return (
    <div className="sidebar-container">
      <h2 className="ui medium top attached header mt-0">{i18next.t('Versions')}</h2>
      <div id="record-versions" className="ui segment rdm-sidebar bottom attached pl-0 pr-0 pt-0">
        <div className="versions">
          <div id="recordVersions" data-record={record} data-preview={isPreview}>
            <RecordVersionsList record={record} isPreview={isPreview} />
          </div>
        </div>
      </div>
    </div>
  );
};

export {
    VersionsSection
}