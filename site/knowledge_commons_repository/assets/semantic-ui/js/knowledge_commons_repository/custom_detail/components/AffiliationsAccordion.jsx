import React from 'react';
import { i18next } from '@translations/invenio_app_rdm/i18next';

const AffiliationsAccordion = ({group, affiliations, iconsRor}) => {

  return (
    <>
      <div className="ui sixteen wide tablet three wide computer column title right aligned bottom aligned">
        <button className="ui affiliations-button trigger button mini mr-0"
                aria-controls={`${group}-affiliations`}
                data-open-text={i18next.t('Show affiliations')}
                data-close-text={i18next.t('Hide affiliations')}
                aria-expanded="false"
        >
          {i18next.t("Show affiliations")}
        </button>
      </div>

      <section className="ui sixteen wide column content"
        id={`${group}-affiliations`}
        aria-label={`${i18next.t('Affiliations for')} ${group}`}
      >
        <ul>
        {affiliations.map(
          affiliation => (
            <li key={`${affiliation[0]}.${affiliation[1]}`}>
            {affiliation[0]}.
            {!!affiliation[2] ? (
              <a className="no-text-decoration"
                href={`https://ror.org/${affiliation[2]}`}
                aria-label={`${affiliation[1]}'s ROR ${i18next.t('profile')}`}
                title={`${affiliation[1]}'s ROR ${i18next.t('profile')}`}
              >
                  <img className="ml-5 inline-id-icon" src={iconsRor} alt="ROR icon"/>
              </a>
            ) : ""
            }
            {affiliation[1]}
            </li>
          )
        )}
        </ul>
      </section>
    </>
  )
}

export { AffiliationsAccordion };