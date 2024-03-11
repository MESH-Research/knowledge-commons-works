
import React from 'react';
import i18next from 'i18next';

const AccessStatusLabel = () => {
  <div
    class="ui label small horizontal access-status restricted"
    title={ i18next.t('Collection visibility') }
    data-tooltip={ i18next.t('The collection is restricted to users with access.') }
    data-inverted=""
    data-position="top right"
  >
    <i class="icon ban" aria-hidden="true"></i> {i18next.t("Restricted") }
  </div>
};

export { AccessStatusLabel };