import React from "react";
import { i18next } from "@translations/invenio_app_rdm/i18next";
import { Accordion, Icon } from "semantic-ui-react";
import { Creatibutors } from "./Creatibutors";
import { Doi } from "../components/Doi";
import { toPidUrl } from "../util";
import { Analytics } from "./Analytics";

function getCustomFieldComponents({
  sectionFields,
  customFields,
  detailOrder,
}) {
  console.log("****getCustomFieldComponents sectionFields", sectionFields);
  console.log("****getCustomFieldComponents customFields", customFields);
  console.log("****getCustomFieldComponents detailOrder", detailOrder);
  if (detailOrder) {
    sectionFields = detailOrder.map(({ section, subsections }) =>
      sectionFields.find((fieldCfg) => fieldCfg.field === section)
    );
  }

  return sectionFields.map((fieldCfg) => {
    console.log("****getCustomFieldComponents fieldCfg", fieldCfg);
    const fieldValue = customFields[fieldCfg.field];
    if (!!fieldValue) {
      console.log("****getCustomFieldComponents fieldValue", fieldValue);
      if (typeof fieldValue === "object") {
        let entries = Object.entries(fieldValue);
        console.log("****getCustomFieldComponents entries", entries);
        const orderSubsections = detailOrder.find(
          ({ section }) => section === fieldCfg.field
        )?.subsections;
        console.log(
          "****getCustomFieldComponents orderSubsections",
          orderSubsections
        );
        if (orderSubsections) {
          entries = orderSubsections.reduce((acc, { section }) => {
            const match = entries.find(([key, value]) => key === section);
            return match ? [...acc, match] : acc;
          }, []);
        }
        console.log("****getCustomFieldComponents entries", entries);
        return (
          <>
            {entries.map(([key, value]) => (
              <DetailItem
                key={key}
                title={fieldCfg.props[key].label}
                value={value}
                trueLabel={fieldCfg.props[key].trueLabel}
                falseLabel={fieldCfg.props[key].falseLabel}
                isVocabulary={fieldCfg.props[key].isVocabulary}
              />
            ))}
          </>
        );
      } else {
        return (
          <DetailItem
            key={fieldCfg.field}
            title={fieldCfg.props.label}
            value={fieldValue}
            trueLabel={fieldCfg.props.trueLabel}
            falseLabel={fieldCfg.props.falseLabel}
            isVocabulary={fieldCfg.props.isVocabulary}
          />
        );
      }
    } else {
      return null;
    }
  });
}

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

const AdditionalDates = ({ dates }) => {
  return (
    <>
      {dates.map(({ type, date: dateValue, description }, index) => (
        <React.Fragment key={type.title_l10n}>
          <dt className="ui tiny header">{type.title_l10n}</dt>
          <dd>
            {dateValue}
            {description && (
              <span className="text-muted"> ({description})</span>
            )}
          </dd>
        </React.Fragment>
      ))}
    </>
  );
};

const FundingItem = ({ item, index }) => {
  const { award, funder } = item;

  if (award) {
    const { title_l10n, number, identifiers } = award;

    return (
      <dl class="details-list mt-0">
        {title_l10n && (
          <dt className="ui tiny header">
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
          </dt>
        )}
        {funder && <dd className="text-muted">{funder.name}</dd>}
      </dl>
    );
  } else {
    return <h4 className="ui tiny header">{funder.name}</h4>;
  }
};

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
        <React.Fragment key={relationType}>
          <dt className="ui tiny header">{relationType}</dt>
          <IdentifiersForGroup
            identifiers={identifiers}
            identifierSchemes={identifierSchemes}
            landingUrls={landingUrls}
          />
        </React.Fragment>
      ))}
    </>
  );
}

const DOITextLink = ({ doi, doiLink }) => {
  return (
    <>
      <dt className="ui tiny header">DOI</dt>
      <dd key={doi}>
        <a href={doiLink} target="_blank" title={_("Opens in new tab")}>
          {doi}
        </a>
      </dd>
    </>
  );
};

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
      <React.Fragment key={scheme}>
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
      </React.Fragment>
    ));
};

const TitleDetail = ({ titleType, titleLang, title }) => {
  return (
    <React.Fragment key={title}>
      <dt className="ui tiny header">
        {titleType}
        {titleLang && (
          <span className="language text-muted">{` (${titleLang})`}</span>
        )}
      </dt>
      <dd>{title}</dd>
    </React.Fragment>
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
const getDetailsComponents = ({
  customFieldsUi,
  detailOrder,
  doiBadgeUrl,
  hasFiles,
  iconsHcUsername,
  iconsGnd,
  iconsOrcid,
  iconsRor,
  identifierSchemes,
  landingUrls,
  localizedStats,
  record,
  showDecimalSizes,
}) => {
  const idDoi = record.pids.doi ? record.pids.doi.identifier : null;
  console.log("****getDetailsComponents record", record);
  const detailsInfo = [
    {
      title: i18next.t("Analytics"),
      value: (
        <Analytics
          record={record}
          hasFiles={hasFiles}
          localizedStats={localizedStats}
          showDecimalSizes={showDecimalSizes}
        />
      ),
    },
    {
      title: i18next.t("Contributors"),
      value: (
        <Creatibutors
          creators={record.ui.creators}
          contributors={record.ui.contributors}
          iconsRor={iconsRor}
          iconsOrcid={iconsOrcid}
          iconsHcUsername={iconsHcUsername}
          iconsGnd={iconsGnd}
          landingUrls={landingUrls}
        />
      ),
    },
    {
      title: i18next.t("DOI badge"),
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
      title: i18next.t("DOI"),
      value:
        idDoi !== null ? (
          <DOITextLink doiLink={record.links.doi} doi={idDoi} />
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

  return detailsComponentArray.length > 0 ? detailsComponentArray : null;
};

const DetailItem = ({ title, value, trueLabel, falseLabel, isVocabulary }) => {
  let valueComponent = <dd></dd>;
  if (typeof value === "string") {
    valueComponent = <dd dangerouslySetInnerHTML={{ __html: value }} />;
  } else if (typeof value === "boolean") {
    valueComponent = <dd>{value ? trueLabel : falseLabel}</dd>;
  } else if (isVocabulary) {
    valueComponent = <dd>{value.join(", ")}</dd>;
  } else if (
    Array.isArray(value) &&
    value.length > 0 &&
    typeof value[0] === "string"
  ) {
    valueComponent = <dd>{value.join(", ")}</dd>;
  } else {
    valueComponent = <dd>{value}</dd>;
  }

  return (
    <>
      <dt className="ui tiny header">{title}</dt>
      {valueComponent}
    </>
  );
};

const ConferenceDetailSection = ({ conference }) => {
  let titlePiece = conference.url ? (
    <a href={conference.url}>
      <i className="fa fa-external-link"></i> {conference.title}
    </a>
  ) : (
    `"${conference.title}"`
  );
  let conferencePieces = [
    titlePiece,
    conference.place,
    conference.dates,
    conference.session,
    conference.session_part,
  ];
  conferencePieces = conferencePieces.filter((piece) => piece);

  return (
    <>
      <dt className="ui tiny header">Event</dt>
      <dd>{conferencePieces.join(", ")}</dd>
      {conference.url && !conference.title && (
        <>
          <dt className="ui tiny header">Event</dt>
          <dd>
            <a href={conference.url}>
              <i className="fa fa-external-link"></i>{" "}
              {i18next.t("Conference website")}
            </a>
          </dd>
        </>
      )}
    </>
  );
};

const PublishingDetails = ({
  customFieldsUi,
  doiBadgeUrl,
  hasFiles,
  iconsHcUsername,
  iconsGnd,
  iconsOrcid,
  iconsRor,
  identifierSchemes,
  landingUrls,
  localizedStats,
  record,
  section,
  show: showWhole,
  showDecimalSizes,
  showAccordionIcons = false,
  subsections: accordionSections,
}) => {
  const [activeIndex, setActiveIndex] = React.useState([0]);
  console.log("****PublishingDetails record", record);
  console.log("****PublishingDetails customFieldsUi", customFieldsUi);
  const customFieldSectionNames = customFieldsUi.map(({ section }) => section);
  const sectionsArray = accordionSections.reduce(
    (acc, { section: sectionTitle, subsections, icon, show }) => {
      if (customFieldSectionNames.includes(sectionTitle)) {
        const detailOrder = subsections;
        const sectionCustomFields = customFieldsUi.find(
          ({ section }) => section === sectionTitle
        );
        const fieldContent = getCustomFieldComponents({
          sectionFields: sectionCustomFields.fields,
          customFields: record.custom_fields,
          detailOrder: detailOrder,
        });
        console.log("****PublishingDetails fieldContent", fieldContent);
        if (fieldContent[0]) {
          acc.push({
            key: sectionTitle,
            title: { content: sectionTitle, icon: sectionCustomFields.icon },
            content: {
              content: fieldContent,
            },
          });
        }
      } else {
        const detailOrder = subsections?.map(({ section }) => section);
        acc.push({
          title: { content: sectionTitle, icon: icon },
          content: {
            content: getDetailsComponents({
              customFieldsUi: customFieldsUi,
              detailOrder: detailOrder,
              doiBadgeUrl: doiBadgeUrl,
              hasFiles: hasFiles,
              iconsHcUsername: iconsHcUsername,
              iconsGnd: iconsGnd,
              iconsOrcid: iconsOrcid,
              iconsRor: iconsRor,
              identifierSchemes: identifierSchemes,
              landingUrls: landingUrls,
              localizedStats: localizedStats,
              record: record,
              showDecimalSizes: showDecimalSizes,
            }),
          },
          show: show,
        });
      }
      return acc;
    },
    []
  );
  console.log("****PublishingDetails sectionsArray", sectionsArray);

  const handleHeaderClick = (index) => {
    const newIndex = activeIndex.includes(index)
      ? activeIndex.filter((i) => i !== index)
      : [...activeIndex, index];
    setActiveIndex(newIndex);
  };

  return (
    <Accordion fluid exclusive={false} defaultActiveIndex={[0]}>
      {sectionsArray.map(
        ({ title, content, show }, idx) =>
          content.content && (
            <>
              <Accordion.Title
                active={activeIndex.includes(idx)}
                index={idx}
                onClick={() => handleHeaderClick(idx)}
                className={`${title.content} ${show}`}
              >
                <Icon
                  name={
                    !!title.icon && !!showAccordionIcons
                      ? title.icon
                      : "dropdown"
                  }
                />
                {title.content}
              </Accordion.Title>
              <Accordion.Content
                active={activeIndex.includes(idx)}
                className={`${title.content} ${show}`}
              >
                <dl className="details-list mt-0">
                  {content.content.map((component) => component)}
                </dl>
              </Accordion.Content>
            </>
          )
      )}
    </Accordion>
  );
};

export { PublishingDetails, getDetailsComponents };
