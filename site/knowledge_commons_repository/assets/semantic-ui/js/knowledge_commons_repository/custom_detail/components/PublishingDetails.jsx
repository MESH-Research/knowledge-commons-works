import React from "react";
import { i18next } from "@translations/invenio_app_rdm/i18next";
import { Doi } from "../components/Doi";

/** Function to get the list of publication details for display.
 *
 * @param {*} record The record object
 * @param {*} doiBadgeUrl The URL of the DOI badge image
 * @param {*} detailOrder The order of the details to display. An array
 *  of strings that should match titles in the detailsInfo list within
 *  this function.
 * @returns Array of objects with title and value. The values are React components.
 */
const getDetailsInfo = (record, doiBadgeUrl, detailOrder) => {
  const idDoi = record.pids.doi.identifier;
  let detailsInfo = [
    {
      tile: i18next.t("DOI"),
      value: !!idDoi ? (
        <Doi
          idDoi={record.pids.doi.identifier}
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
  ];
  detailsInfo = detailsInfo.filter(
    ({ title, value }) => value !== null && detailOrder.includes(title)
  );
  const sortedDetailsInfo = detailsInfo.toSorted(
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

const PublishingDetails = ({ record, doiBadgeUrl, section, subsections }) => {
  const detailOrder = subsections.map(({ section }) => section);
  const detailsInfo = getDetailsInfo(record, doiBadgeUrl, detailOrder);
  return (
    <dl className="details-list mt-0">
      {detailsInfo.map((component) => component)}
    </dl>
  );
};

export { PublishingDetails, getDetailsInfo };
