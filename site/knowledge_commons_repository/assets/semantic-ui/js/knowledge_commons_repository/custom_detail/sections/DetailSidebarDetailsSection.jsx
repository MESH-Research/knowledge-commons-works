import React from 'react';
import { i18next } from '@translations/invenio_app_rdm/i18next';
import { Doi } from '../components/Doi';

const ConferenceDetailSection = ({conference}) => {
  return (
    <>
     <dd>
       {conference.url ? (
        <a href={conference.url}><i className="fa fa-external-link"></i> {conference.title}</a>
       ) : (
        conference.title
       )}
       {conference.place && `${conference.place}`}
       {conference.dates && `${conference.dates}`}
       {conference.session && `Session ${conference.session}`}
       {conference.session_part && `Part ${conference.session_part}`}
     </dd>
     {conference.url && !conference.title && (
       <dd><a href={conference.url}><i className="fa fa-external-link"></i> {i18next.t('Conference website')}</a></dd>
     )}
    </>
  );
};

const SidebarDetailsSection = ({record, doiBadgeUrl}) => {
  const idDoi = record.pids.doi.identifier;
  let details = [
    {title: i18next.t('Resource type'), value: record.ui.resource_type.title_l10n},
    {title: i18next.t('Publication date'), value: record.ui.publication_date_l10n_long},
    {title: i18next.t('Publisher'), value: record.metadata.publisher},
    {title: i18next.t('Published in'), value: (record.ui.publishing_information && record.ui.publishing_information.journal) ? record.ui.publishing_information.journal : null},
    {title: i18next.t('Imprint'), value: (record.ui.publishing_information && record.ui.publishing_information.imprint) ? record.ui.publishing_information.imprint : null},
    {title: i18next.t('Awarding university'), "value":(record.ui.publishing_information && record.ui.publishing_information.thesis) ? record.ui.publishing_information.thesis : null},
    {title: i18next.t('Conference'), "value": record.ui.conference ? <ConferenceDetailSection conference={record.ui.conference} /> : null},
    {title: i18next.t('Languages'), "value": record.ui.languages ? record.ui.languages.join(',') : null},
    {title: i18next.t('Formats'), "value": record.metadata.formats ? record.metadata.formats.join(',') : null},
    {title: i18next.t('Sizes'), "value": record.metadata.sizes ? record.metadata.sizes.join(',') : null},
  ]
  details = details.filter(({value}) => value !== null);

  return (
    <div className="sidebar-container" aria-label={i18next.t('Publication details')}>
      {/* <h2 className="ui medium top attached header mt-0">{i18next.t('Details')}</h2> */}
      <div id="record-details" className="ui segment bottom attached rdm-sidebar">

        {!!idDoi && <Doi idDoi={idDoi} doiBadgeUrl={doiBadgeUrl} doiLink={record.links.doi} />}

        <dl className="details-list mt-0">
          {details.map(({title, value}) => (
            <>
              <dt className="ui tiny header">{title}</dt>
              <dd>{value}</dd>
            </>
          ))}
        </dl>

        {record.ui.resource_type && (
          <span className="ui label horizontal small neutral mb-5"
                title={i18next.t('Resource type')}>{record.ui.resource_type.title_l10n}</span>
        )}

        <span className={`ui label horizontal small access-status ${record.ui.access_status.id} mb-5`}
              title={i18next.t('Access status')}
              data-tooltip={record.ui.access_status.description_l10n}
              data-inverted=""
        >
          {record.ui.access_status.icon && (
            <i className={`icon ${record.ui.access_status.icon}`}></i>
          )}
          {record.ui.access_status.title_l10n}
        </span>
      </div>
    </div>
  );
};

export {
    SidebarDetailsSection,
    ConferenceDetailSection
}