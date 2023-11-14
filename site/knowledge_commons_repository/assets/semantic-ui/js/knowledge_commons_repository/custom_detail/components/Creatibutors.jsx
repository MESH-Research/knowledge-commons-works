import React from "react";
import { i18next } from "@translations/invenio_app_rdm/i18next";
import { Card, Icon, Label, List } from "semantic-ui-react";
import { AffiliationsAccordion } from "./AffiliationsAccordion";

const IdentifiersList = (ids) => {
  if (ids !== undefined) {
    // ids = creatibutor.person_or_org.identifiers.group(({scheme}) => scheme);
    ids = ids.reduce((x, y) => {
      (x[y.scheme] = x[y.scheme] || []).push(y);
      return x;
    }, {});
    ids = Object.values(ids).reduce((acc, idlist) => [...acc, ...idlist], []);
  } else {
    ids = [];
  }
  return ids;
};

const makeSchemeStrings = (
  iconsGnd,
  iconsHcUsername,
  iconsOrcid,
  iconsRor,
  landingUrls
) => {
  const mystrings = {
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
  console.log("****makeSchemeStrings mystrings", mystrings);
  return mystrings;
};

const CreatibutorIcon = ({
  creatibutor,
  iconsRor,
  iconsOrcid,
  iconsGnd,
  iconsHcUsername,
  landingUrls,
}) => {
  let ids = IdentifiersList(creatibutor.person_or_org.identifiers);
  const schemeStrings = makeSchemeStrings(
    iconsGnd,
    iconsHcUsername,
    iconsOrcid,
    iconsRor,
    landingUrls
  );
  return (
    <>
      {!!ids
        ? ids.map(({ scheme, identifier }) => (
            <a
              href={`${schemeStrings[scheme][2]}${identifier}`}
              className="no-text-decoration"
              key={`${scheme}-${identifier}`}
              aria-label={`${creatibutor.person_or_org.name}'s ${
                schemeStrings[scheme][0]
              } ${i18next.t("profile")}`}
            >
              <img
                className="ml-5 inline-id-icon"
                src={schemeStrings[scheme][1]}
                alt={`${schemeStrings[scheme][0]} icon`}
                title={`${creatibutor.person_or_org.name}'s ${
                  schemeStrings[scheme][0]
                } ${i18next.t("profile")}`}
              />
            </a>
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
  show_ids = true,
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
      {!!show_ids && creatibutor?.person_or_org?.identifiers && (
        <CreatibutorIcon
          creatibutor={creatibutor}
          iconsRor={iconsRor}
          iconsOrcid={iconsOrcid}
          iconsGnd={iconsGnd}
          iconsHcUsername={iconsHcUsername}
          landingUrls={landingUrls}
        />
      )}
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
      {/* <dt className="hidden">{i18next.t("Creators")}</dt> */}
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
  console.log("****Creatibutors creators", creators.creators);
  console.log("****Creatibutors contributors", contributors);
  const creatibutors =
    contributors !== undefined
      ? creators?.creators?.concat(contributors?.contributors)
      : creators?.creators;
  console.log("****Creatibutors creatibutors", creatibutors);
  let ids = creatibutors.reduce((acc, creatibutor) => {
    acc[creatibutor.person_or_org.name] = IdentifiersList(
      creatibutor.person_or_org.identifiers
    );
    return acc;
  }, {});
  const schemeStrings = makeSchemeStrings(
    iconsGnd,
    iconsHcUsername,
    iconsOrcid,
    iconsRor,
    landingUrls
  );
  return (
    <div className="">
      {creatibutors?.map((creator) => (
        <Card fluid>
          <Card.Content className="pb-5">
            <Card.Header>
              <Creatibutor
                creatibutor={creator}
                key={creator.person_or_org.name}
                show_affiliations={show_affiliations}
                show_ids={false}
                iconsRor={iconsRor}
                iconsOrcid={iconsOrcid}
                iconsGnd={iconsGnd}
                iconsHcUsername={iconsHcUsername}
                landingUrls={landingUrls}
              />
            </Card.Header>
            <Card.Meta>
              {!!creator.role && <span>{creator.role.title}</span>}
            </Card.Meta>
            <Card.Description className="mt-0">
              {!!creator.affiliations && show_affiliations && (
                <small>{creator.affiliations.map((a) => a[1]).join(",")}</small>
              )}
            </Card.Description>
          </Card.Content>
          <Card.Content extra className="mt-0 pt-5">
            {ids[creator.person_or_org.name]?.map(({ scheme, identifier }) => (
              <a
                href={`${schemeStrings[scheme][2]}${identifier}`}
                className="no-text-decoration"
                key={`${scheme}-${identifier}`}
                aria-label={`${creator.person_or_org.name}'s ${
                  schemeStrings[scheme][0]
                } ${i18next.t("profile")}`}
              >
                <img
                  className="mr-5 inline-id-icon"
                  src={schemeStrings[scheme][1]}
                  alt={`${schemeStrings[scheme][0]} icon`}
                  title={`${creator.person_or_org.name}'s ${
                    schemeStrings[scheme][0]
                  } ${i18next.t("profile")}`}
                />
                <small>
                  {scheme === "hc_username" ? "Humanities Commons" : scheme}{" "}
                  {i18next.t("profile")}
                </small>
              </a>
            ))}
          </Card.Content>
        </Card>
      ))}
    </div>
  );
};

export { Creatibutors, CreatibutorsShortList };
