import React from "react";
import { i18next } from "@translations/invenio_app_rdm/i18next";
import { Accordion, Icon } from "semantic-ui-react";
import { Doi } from "../components/Doi";
import { toPidUrl } from "../util";

const References = ({ references, identifierSchemes }) => {
  return (
    <>
      {references.map(({ reference, identifier, scheme }, index) => (
        <dd>
          {reference.reference}
          {identifier &&
            (scheme
              ? ` (${identifierSchemes[scheme]} - ${identifier})`
              : ` (${identifier})`)}
        </dd>
      ))}
    </>
  );
};

function AdditionalDates({ dates }) {
  return (
    <>
      {dates.map(({ type, date: dateValue, description }, index) => (
        <>
          <dt className="ui tiny header">{type.title_l10n}</dt>
          <dd>
            <div>{dateValue}</div>
            {description && <div className="text-muted">{description}</div>}
          </dd>
        </>
      ))}
    </>
  );
}

function FundingItem({ item, index }) {
  const { award, funder } = item;

  if (award) {
    const { title_l10n, number, identifiers } = award;

    return (
      <div>
        {title_l10n && (
          <h4 className="ui tiny header">
            <span className="mr-5">{title_l10n}</span>
            {number && (
              <span
                className="ui mini basic label ml-0 mr-5"
                id={`number-label-${index}`}
              >
                {number}
              </span>
            )}
            {identifiers &&
              identifiers
                .filter((identifier) => identifier.scheme === "url")
                .map((identifier) => (
                  <a
                    key={identifier.identifier}
                    href={identifier.identifier}
                    target="_blank"
                    rel="noopener noreferrer"
                    aria-label={i18next.t("Open external link")}
                  >
                    <i className="external alternate icon"></i>
                  </a>
                ))}
          </h4>
        )}
        {funder && <p className="text-muted">{funder.name}</p>}
      </div>
    );
  } else {
    return <h4 className="ui tiny header">{funder.name}</h4>;
  }
}

function Funding({ funding }) {
  return (
    <>
      {funding.map((item, index) => (
        <FundingItem key={index} item={item} index={index} />
      ))}
    </>
  );
}

function IdentifiersForGroup({ identifiers, identifierSchemes, landingUrls }) {
  return (
    <>
      {identifiers.map(({ scheme, identifier, resource_type }) => (
        <dd key={identifier}>
          {scheme && (
            <span className="text-muted">{`${identifierSchemes[scheme]}: `}</span>
          )}
          {identifier && (
            <>
              <a
                href={toPidUrl(identifier, scheme, landingUrls)}
                target="_blank"
                title={i18next.t("Opens in new tab")}
              >
                {identifier}
              </a>
              {resource_type && ` (${resource_type.title_l10n})`}
            </>
          )}
        </dd>
      ))}
    </>
  );
}

function RelatedIdentifiers({
  relatedIdentifiers,
  identifierSchemes,
  landingUrls,
}) {
  const groups = Object.groupBy(
    relatedIdentifiers,
    ({ relation_type }) => relation_type.title_l10n
  );

  return (
    <>
      {Object.entries(groups).map(([relationType, identifiers]) => (
        <>
          <dt className="ui tiny header">{relationType}</dt>
          <IdentifiersForGroup
            identifiers={identifiers}
            identifierSchemes={identifierSchemes}
            landingUrls={landingUrls}
          />
        </>
      ))}
    </>
  );
}

const URLs = ({ identifiers }) => {
  return (
    <>
      <dt className="ui tiny header">URLs</dt>
      {identifiers
        .filter(({ scheme }) => scheme === "url")
        .map(({ identifier }) => (
          <dd key={identifier}>
            {identifier && (
              <a
                href={identifier}
                target="_blank"
                title={_("Opens in new tab")}
              >
                {identifier}
              </a>
            )}
          </dd>
        ))}
    </>
  );
};

const AlternateIdentifiers = ({
  alternateIdentifiers,
  identifierSchemes,
  landingUrls,
}) => {
  const groups = Object.groupBy(alternateIdentifiers, ({ scheme }) => scheme);
  return Object.keys(groups)
    .filter((scheme) => scheme !== "url")
    .map((scheme) => (
      <>
        <dt className="ui tiny header">{identifierSchemes[scheme]}</dt>
        {groups[scheme].map(({ scheme, identifier }) => (
          <dd key={identifier}>
            {identifier && (
              <a
                href={toPidUrl(identifier, scheme, landingUrls)}
                target="_blank"
                title={_("Opens in new tab")}
              >
                {identifier}
              </a>
            )}
          </dd>
        ))}
      </>
    ));
};

const TitleDetail = ({ titleType, titleLang, title }) => {
  return (
    <>
      <dt className="ui tiny header">
        {titleType}
        {titleLang && (
          <span className="language text-muted">{` (${titleLang})`}</span>
        )}
      </dt>
      <dd>{title}</dd>
    </>
  );
};

const AdditionalTitles = ({ addTitles }) => {
  return (
    <>
      {addTitles.map(({ type, lang, title }) => (
        <TitleDetail
          key={title}
          titleType={type.title_l10n}
          titleLang={lang && lang.title_l10n}
          title={title}
        />
      ))}
    </>
  );
};

/** Function to get the list of publication details for display.
 *
 * @param {*} record The record object
 * @param {*} doiBadgeUrl The URL of the DOI badge image
 * @param {*} detailOrder The order of the details to display. An array
 *  of strings that should match titles in the detailsInfo list within
 *  this function.
 * @returns Array of objects with title and value. The values are React components.
 */
const getDetailsInfo = (
  detailOrder,
  doiBadgeUrl,
  identifierSchemes,
  landingUrls,
  record
) => {
  const idDoi = record.pids.doi ? record.pids.doi.identifier : null;
  const detailsInfo = [
    {
      title: i18next.t("DOI"),
      value:
        idDoi !== null ? (
          <Doi
            idDoi={idDoi}
            doiBadgeUrl={doiBadgeUrl}
            doiLink={record.links.doi}
          />
        ) : null,
    },
    {
      title: i18next.t("Resource type"),
      value: record.ui.resource_type.title_l10n,
    },
    {
      title: i18next.t("Publication date"),
      value: record.ui.publication_date_l10n_long,
    },
    { title: i18next.t("Publisher"), value: record.metadata.publisher },
    {
      title: i18next.t("Published in"),
      value:
        record.ui.publishing_information &&
        record.ui.publishing_information.journal
          ? record.ui.publishing_information.journal
          : null,
    },
    {
      title: i18next.t("Imprint"),
      value:
        record.ui.publishing_information &&
        record.ui.publishing_information.imprint
          ? record.ui.publishing_information.imprint
          : null,
    },
    {
      title: i18next.t("Awarding university"),
      value:
        record.ui.publishing_information &&
        record.ui.publishing_information.thesis
          ? record.ui.publishing_information.thesis
          : null,
    },
    {
      title: i18next.t("Conference"),
      value: record.ui.conference ? (
        <ConferenceDetailSection conference={record.ui.conference} />
      ) : null,
    },
    {
      title: i18next.t("Languages"),
      value: record.ui.languages
        ? record.ui.languages.map(({ title_l10n }) => title_l10n).join(",")
        : null,
    },
    {
      title: i18next.t("Formats"),
      value: record.metadata.formats ? record.metadata.formats.join(",") : null,
    },
    {
      title: i18next.t("Sizes"),
      value: record.metadata.sizes ? record.metadata.sizes.join(",") : null,
    },
    {
      title: i18next.t("Additional titles"),
      value: record.ui.additional_titles ? (
        <AdditionalTitles addTitles={record.ui.additional_titles} />
      ) : null,
    },
    {
      title: i18next.t("URLs"),
      value: record.metadata.identifiers?.filter(
        (id) => id.scheme === "url"
      ) ? (
        <URLs identifiers={record.metadata.identifiers} />
      ) : null,
    },
    {
      title: i18next.t("Alternate identifiers"),
      value: record.metadata.identifiers?.filter(
        (id) => id.scheme !== "url"
      ) ? (
        <AlternateIdentifiers
          alternateIdentifiers={record.metadata.identifiers}
          identifierSchemes={identifierSchemes}
          landingUrls={landingUrls}
        />
      ) : null,
    },
    {
      title: i18next.t("Related identifiers"),
      value: record.ui.related_identifiers ? (
        <RelatedIdentifiers
          relatedIdentifiers={record.ui.related_identifiers}
          identifierSchemes={identifierSchemes}
          landingUrls={landingUrls}
        />
      ) : null,
    },
    {
      title: i18next.t("Funding"),
      value: record.ui.funding ? <Funding funding={record.ui.funding} /> : null,
    },
    {
      title: i18next.t("Additional dates"),
      value: record.ui.dates ? (
        <AdditionalDates dates={record.ui.dates} />
      ) : null,
    },
    {
      title: i18next.t("References"),
      value: record.ui.references ? (
        <References
          references={record.ui.references}
          identifierSchemes={identifierSchemes}
        />
      ) : null,
    },
  ];
  const filteredDetailsInfo = detailsInfo.filter(
    ({ title, value }) =>
      (typeof value === "string" || React.isValidElement(value)) &&
      detailOrder.includes(title)
  );
  const sortedDetailsInfo = filteredDetailsInfo.toSorted(
    (a, b) => detailOrder.indexOf(a.title) - detailOrder.indexOf(b.title)
  );

  const detailsComponentArray = sortedDetailsInfo.map(({ title, value }) =>
    typeof value === "string" ? (
      <DetailItem title={title} value={value} key={title} />
    ) : (
      value
    )
  );

  return detailsComponentArray;
};

const DetailItem = ({ title, value }) => {
  return (
    <>
      <dt className="ui tiny header">{title}</dt>
      <dd>{value}</dd>
    </>
  );
};

const ConferenceDetailSection = ({ conference }) => {
  return (
    <>
      <dd>
        {conference.url ? (
          <a href={conference.url}>
            <i className="fa fa-external-link"></i> {conference.title}
          </a>
        ) : (
          conference.title
        )}
        {conference.place && `${conference.place}`}
        {conference.dates && `${conference.dates}`}
        {conference.session && `Session ${conference.session}`}
        {conference.session_part && `Part ${conference.session_part}`}
      </dd>
      {conference.url && !conference.title && (
        <dd>
          <a href={conference.url}>
            <i className="fa fa-external-link"></i>{" "}
            {i18next.t("Conference website")}
          </a>
        </dd>
      )}
    </>
  );
};

const PublishingDetails = ({
  doiBadgeUrl,
  identifierSchemes,
  landingUrls,
  record,
  section,
  subsections: accordionSections,
}) => {
  const [activeIndex, setActiveIndex] = React.useState(0);
  console.log("****PublishingDetails record", record);
  const sectionsArray = accordionSections.map(
    ({ section: sectionTitle, subsections }) => {
      const detailOrder = subsections.map(({ section }) => section);
      return {
        title: sectionTitle,
        components: getDetailsInfo(
          detailOrder,
          doiBadgeUrl,
          identifierSchemes,
          landingUrls,
          record
        ),
      };
    }
  );
  return (
    <Accordion styled fluid>
      {sectionsArray.map(({ title, components }, idx) => (
        <>
          <Accordion.Title
            active={activeIndex === idx}
            index={idx}
            onClick={() => setActiveIndex(idx)}
          >
            <Icon name="dropdown" />
            {title}
          </Accordion.Title>
          <Accordion.Content active={activeIndex === idx}>
            <dl className="details-list mt-0">
              {components.map((component) => component)}
            </dl>
          </Accordion.Content>
        </>
      ))}
    </Accordion>
  );
};

export { PublishingDetails, getDetailsInfo };
