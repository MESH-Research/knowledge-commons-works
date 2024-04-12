
import React from 'react';
import { i18next } from '@translations/invenio_rdm_records/i18next';

const AccessStatusLabel = () => {
  return(
    <div
      className="ui label small horizontal access-status restricted"
      title={ i18next.t('Collection visibility') }
      data-tooltip={ i18next.t('The collection is restricted to users with access.') }
      data-inverted=""
      data-position="top right"
    >
      <i className="icon ban" aria-hidden="true"></i> {i18next.t("Restricted") }
    </div>
  )
};

export { AccessStatusLabel };