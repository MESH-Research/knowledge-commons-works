import React from "react";
import { i18next } from "@translations/invenio_app_rdm/i18next";
import { Icon, Image, Label, List } from "semantic-ui-react";
import { AffiliationsAccordion } from "./AffiliationsAccordion";

const CreatibutorIcon = ({
  creatibutor,
  iconsRor,
  iconsOrcid,
  iconsGnd,
  iconsHcUsername,
  landingUrls,
}) => {
  let ids = creatibutor.person_or_org.identifiers;
  if (creatibutor.person_or_org.identifiers !== undefined) {
    // ids = creatibutor.person_or_org.identifiers.group(({scheme}) => scheme);
    ids = ids.reduce((x, y) => {
      (x[y.scheme] = x[y.scheme] || []).push(y);
      return x;
    }, {});
    ids = Object.values(ids).reduce((acc, idlist) => [...acc, ...idlist], []);
  }
  const schemeStrings = {
    orcid: ["ORCID", iconsOrcid, landingUrls.orcid],
    ror: ["ROR", iconsRor, landingUrls.ror],
    gnd: ["GND", iconsGnd, landingUrls.gnd],
    hc_username: [
      "Humanities Commons",
      // FIXME: temporary until we get a proper icon
      iconsHcUsername.replace(".svg", ".jpg"),
      landingUrls.hcommons_username,
    ],
  };
  return (
    <>
      {!!ids
        ? ids.map(({ scheme, identifier }) => (
            <Image
              as={"a"}
              className="no-text-decoration ml-5"
              key={`${scheme}-${identifier}`}
              src={schemeStrings[scheme][1]}
              href={`${schemeStrings[scheme][2]}${identifier}`}
              aria-label={`${creatibutor.person_or_org.name}'s ${
                schemeStrings[scheme][0]
              } ${i18next.t("profile")}`}
              alt={`${schemeStrings[scheme][0]} icon`}
              title={`${creatibutor.person_or_org.name}'s ${
                schemeStrings[scheme][0]
              } ${i18next.t("profile")}`}
            />
          ))
        : ""}
      {!!ids && creatibutor.person_or_org.type == "organizational" ? (
        <Icon name="group" />
      ) : (
        ""
      )}
    </>
  );
};

const Creatibutor = ({
  creatibutor,
  show_affiliations,
  show_roles,
  iconsRor,
  iconsOrcid,
  iconsGnd,
  iconsHcUsername,
  itemIndex,
  listLength,
  landingUrls,
}) => {
  let extra_props = {};
  if (show_affiliations && creatibutor.affiliations) {
    extra_props["data-tooltip"] = creatibutor.affiliations
      .map((a) => a[1])
      .join("; ");
  }
  return (
    <dd className="creatibutor-wrap separated">
      <List.Content as={"span"} className="creatibutor-name">
        <a
          className="ui creatibutor-link"
          href={`../search?q='metadata.creators.person_or_org.name:${creatibutor.person_or_org.name}'`}
          {...extra_props}
        >
          <span>
            {creatibutor.person_or_org.type === "personal" &&
            creatibutor.person_or_org.family_name
              ? `${creatibutor.person_or_org.given_name} ${creatibutor.person_or_org.family_name}`
              : creatibutor.person_or_org.name}
          </span>
        </a>
      </List.Content>
      {!!show_roles &&
      creatibutor.role &&
      creatibutor.role.title !== "Other" ? (
        <Label className="creatibutor-role">{creatibutor.role.title}</Label>
      ) : (
        ""
      )}
      <CreatibutorIcon
        creatibutor={creatibutor}
        iconsRor={iconsRor}
        iconsOrcid={iconsOrcid}
        iconsGnd={iconsGnd}
        iconsHcUsername={iconsHcUsername}
        landingUrls={landingUrls}
      />
    </dd>
  );
};

const CreatibutorsShortList = ({
  creators,
  contributors,
  iconsRor,
  iconsOrcid,
  iconsGnd,
  iconsHcUsername,
  landingUrls,
}) => {
  const show_affiliations = false;
  const show_roles = false;
  const creatibutors = contributors
    ? creators?.creators?.concat(contributors?.contributors)
    : creators?.creators;
  return (
    <section
      id="creatibutors-list-section"
      className="ui mb-10 mt-10 sixteen wide mobile twelve wide tablet thirteen wide computer column"
    >
      <dt className="hidden">{i18next.t("Creators")}</dt>
      <dl className="creatibutors" aria-label={i18next.t("Contributors list")}>
        {creatibutors?.length
          ? creatibutors.map((creator, idx) => (
              <Creatibutor
                creatibutor={creator}
                key={creator.person_or_org.name}
                show_affiliations={show_affiliations}
                show_roles={show_roles}
                iconsRor={iconsRor}
                iconsOrcid={iconsOrcid}
                iconsGnd={iconsGnd}
                iconsHcUsername={iconsHcUsername}
                landingUrls={landingUrls}
              />
            ))
          : ""}
      </dl>
    </section>
  );
};

const Creatibutors = ({
  creators,
  contributors,
  iconsRor,
  iconsOrcid,
  iconsGnd,
  iconsHcUsername,
  landingUrls,
  section,
  subsections,
}) => {
  const show_affiliations = true;
  console.log("****Creatibutors", creators, contributors);
  const creatibutors = contributors
    ? creators?.creators?.concat(contributors?.contributors)
    : creators?.creators;
  console.log("****Creatibutors creatibutors", creatibutors);
  return (
    <div className="ui grid">
      <div className="row ui accordion affiliations">
        <div className="sixteen wide mobile twelve wide tablet thirteen wide computer column mb-10">
          <dl className="creatibutors" aria-label={i18next.t("Creators list")}>
            <dt className="hidden">{i18next.t("Creators")}</dt>
            {creatibutors?.map((creator) => (
              <Creatibutor
                creatibutor={creator}
                key={creator.person_or_org.name}
                show_affiliations={show_affiliations}
                iconsRor={iconsRor}
                iconsOrcid={iconsOrcid}
                iconsGnd={iconsGnd}
                iconsHcUsername={iconsHcUsername}
                landingUrls={landingUrls}
              />
            ))}
          </dl>
        </div>
      </div>
    </div>
  );
};

export { Creatibutors, CreatibutorsShortList };
