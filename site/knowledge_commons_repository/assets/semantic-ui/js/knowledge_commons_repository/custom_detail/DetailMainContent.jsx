import React from "react";
import i18next from "i18next";

const RecordTitle = ({title}) => {
    return (
      <section
        id="record-title-section"
        aria-label="{{ _('Record title and creators') }}"
      >
        <h1 id="record-title"
          class="wrap-overflowing-text"
        >
          {title}
        </h1>
      </section>
    );
};

const CreatibutorIcon = ({creatibutor}) => {
  const ids = Object.groupby(creatibutor.person_or_org.identifiers,
                            ({scheme}) => scheme);
  const schemeStrings = {'orcid': ['ORCID', 'orcid'],
                         'ror': ['ROR', 'ror-icon'],
                         'gnd': ['GND', 'gnd-icon']};
  return (
    <>
      {ids.map(
        ({scheme, identifier}) => (
          <a class="no-text-decoration"
            href={`${identifier[0]['identifier']|pid_url('orcid')}`}
            aria-label={`${creatibutor.person_or_org.name}'s ${schemeStrings[scheme][0]} ${i18next.t('profile')}`}
            title={`{creatibutor.person_or_org.name}'s ${schemeStrings[scheme][0]} ${i18next.t('profile')}`}
          >
            <img class="ml-5 inline-id-icon"
              src={`url_for('static', filename='images/${schemeStrings[scheme][1]}.svg')`}
              alt={`${schemeStrings[scheme][0]} icon`}
            />
          </a>
      )
      )}
      {(ids.length < 1) && creatibutor.person_or_org.type == 'organizational' && (
        <i class="group icon"></i>
      )}
  </>
)}

const Creatibutor = ({creatibutor, show_affiliations}) => {
  return (
    <dd class="creatibutor-wrap separated">
      <a class="ui creatibutor-link"
        data-tooltip={(show_affiliations && creator.affiliations) ? creatibutor.affiliations.map(a => a['name']).join('; ') : ""}
        href={`api/search?q='metadata.creators.person_or_org.name:${creatibutor.person_or_org.name}'`}
      >
        <span class="creatibutor-name">
          {creatibutor.person_or_org.name}
        </span>
        {creatibutor.affiliations && (
          <sup class="font-tiny">
            {creatibutor.affiliations.map(a => a['name']).join(", ")}
          </sup>
        )}
      </a>
      <CreatibutorIcon creatibutor={creatibutor} />
    </dd>
  );
}

const Creatibutors = ({creators, contributors}) => {
  const show_affiliations = true;
  return(
  <div class="ui grid">
    {(creators && creators.creators.length) ? (
      <div class="row ui accordion affiliations">
        <div class="sixteen wide mobile twelve wide tablet thirteen wide computer column mb-10">
            <dl class="creatibutors" aria-label={i18next.t('Creators list')}>
              <dt class="hidden">{i18next.t('Creators')}</dt>
              {creators.map(
                (creator) => (
                  <Creatibutor creatibutor={creator} show_affiliations={show_affiliations} />
                )
              )}
            </dl>
        </div>

        {creators.affiliations.length ? (
          { affiliations_accordion('creators', creators.affiliations)}}
        ) : ("")}
      </div>
    ) : ("")}

    {(contributors && contributors.contributors.length) ? (
      <div class="row ui accordion affiliations">
        <div class="sixteen wide mobile twelve wide tablet thirteen wide computer column mb-10">
            <dl class="creatibutors" aria-label={i18next.t('Contributors list')}>
              <dt class="hidden">{i18next.t('Contributors')}</dt>
              {contributors.map(
                (contributor) => (
                  <Creatibutor creatibutor={contributor} show_affiliations={show_affiliations} />
                )
              )}
            </dl>
        </div>

        {creators.affiliations.length ? (
          { affiliations_accordion('contributors', contributors.affiliations)}}
        ) : ("")}
      </div>
    ) : ("")}
  </div>
  );
};


const DetailMainContent = ({community,
                            custom_fields_ui,
                            externalResources,
                            files,
                            isDraft,
                            isPreview,
                            record,
                            request,
                            permissions}) => {
    return (
      <>
        <RecordTitle title={record.metadata.title} />
        <Creatibutors
          creators={record.ui.creators}
          contributors={record.ui.contributors}
        />
      </>
    );
};

export default DetailMainContent;