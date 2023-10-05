import React from 'react';
import i18next from 'i18next';
import AffiliationsAccordion from './AffiliationsAccordion';

const CreatibutorIcon = ({creatibutor,
                          iconsRor,
                          iconsOrcid,
                          iconsGnd,
                          iconsHcUsername,
                          landingUrls}
                        ) => {

  let ids = Object.groupBy(creatibutor.person_or_org.identifiers,
                            ({scheme}) => scheme);
  console.log(creatibutor);
  console.log(ids);
  ids = Object.values(ids).reduce((acc, idlist) => [...acc, ...idlist], []);
  const schemeStrings = {'orcid': ['ORCID', iconsOrcid, landingUrls.orcid],
                         'ror': ['ROR', iconsRor, landingUrls.ror],
                         'gnd': ['GND', iconsGnd, landingUrls.gnd],
                         'hc_username': ['Humanities Commons',
                                         iconsHcUsername,
                                         landingUrls.hc_username]};
  return (
    <>
      {ids.map(
        ({scheme, identifier}) => (
          <a className="no-text-decoration"
            key={`${scheme}-${identifier}`}
            href={`${schemeStrings[scheme][2]}${identifier}`}
            aria-label={`${creatibutor.person_or_org.name}'s ${schemeStrings[scheme][0]} ${i18next.t('profile')}`}
            title={`{creatibutor.person_or_org.name}'s ${schemeStrings[scheme][0]} ${i18next.t('profile')}`}
          >
            <img className="ml-5 inline-id-icon"
              src={schemeStrings[scheme][1]}
              alt={`${schemeStrings[scheme][0]} icon`}
            />
          </a>
      )
      )}
      {(ids.length < 1) && creatibutor.person_or_org.type == 'organizational' && (
        <i className="group icon"></i>
      )}
  </>
)}

const Creatibutor = ({creatibutor, show_affiliations,
                      iconsRor,
                      iconsOrcid,
                      iconsGnd,
                      iconsHcUsername,
                      landingUrls}
                    ) => {
  return (
    <dd className="creatibutor-wrap separated">
      <a className="ui creatibutor-link"
        data-tooltip={(show_affiliations && creatibutor.affiliations) ? creatibutor.affiliations.map(a => a['name']).join('; ') : ""}
        href={`api/search?q='metadata.creators.person_or_org.name:${creatibutor.person_or_org.name}'`}
      >
        <span className="creatibutor-name">
          {creatibutor.person_or_org.name}
        </span>
        {creatibutor.affiliations && (
          <sup className="font-tiny">
            {creatibutor.affiliations.map(a => a['name']).join(", ")}
          </sup>
        )}
      </a>
      <CreatibutorIcon creatibutor={creatibutor}
        iconsRor={iconsRor}
        iconsOrcid={iconsOrcid}
        iconsGnd={iconsGnd}
        iconsHcUsername={iconsHcUsername}
        landingUrls={landingUrls}
      />
    </dd>
  );
}

const Creatibutors = ({creators, contributors,
                       iconsRor,
                       iconsOrcid,
                       iconsGnd,
                       iconsHcUsername,
                       landingUrls}) => {
  const show_affiliations = true;
  return(
  <div className="ui grid">
    {(creators && creators.creators.length) ? (
      <div className="row ui accordion affiliations">
        <div className="sixteen wide mobile twelve wide tablet thirteen wide computer column mb-10">
            <dl className="creatibutors" aria-label={i18next.t('Creators list')}>
              <dt className="hidden">{i18next.t('Creators')}</dt>
              {creators.creators.map(
                (creator) => (
                  <Creatibutor
                    creatibutor={creator}
                    key={creator.person_or_org.name}
                    show_affiliations={show_affiliations}
                    iconsRor={iconsRor}
                    iconsOrcid={iconsOrcid}
                    iconsGnd={iconsGnd}
                    iconsHcUsername={iconsHcUsername}
                    landingUrls={landingUrls} />
                )
              )}
            </dl>
        </div>

        {creators.affiliations.length ? (
          <AffiliationsAccordion group='creators'
           affiliations={creators.affiliations}
           iconsRor={iconsRor}
          />
        ) : ("")}
      </div>
    ) : ("")}

    {(contributors && contributors.contributors.length) ? (
      <div className="row ui accordion affiliations">
        <div className="sixteen wide mobile twelve wide tablet thirteen wide computer column mb-10">
            <dl className="creatibutors" aria-label={i18next.t('Contributors list')}>
              <dt className="hidden">{i18next.t('Contributors')}</dt>
              {contributors.contributors.map(
                (contributor) => (
                  <Creatibutor
                    creatibutor={contributor}
                    key={contributor.person_or_org.name}
                    show_affiliations={show_affiliations}
                    iconsRor={iconsRor}
                    iconsOrcid={iconsOrcid}
                    iconsGnd={iconsGnd}
                    iconsHcUsername={iconsHcUsername}
                    landingUrls={landingUrls} />
                )
              )}
            </dl>
        </div>

        {contributors.affiliations.length ? (
          <AffiliationsAccordion group='contributors'
            iconsRor={iconsRor}
            affiliations={contributors.affiliations}
          />
        ) : ("")}
      </div>
    ) : ("")}
  </div>
  );
};

export default Creatibutors;