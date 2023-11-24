import React from "react";
import { Segment } from "semantic-ui-react";
import { SponsoringInstitutionComponent } from "./SponsoringInstitutionComponent";
import { PublicationLocationComponent } from "@js/invenio_modular_deposit_form/field_components/field_components";

const OrganizationDetailsComponent = ({ customFieldsUI }) => {
  return (
    <>
      <SponsoringInstitutionComponent customFieldsUI={customFieldsUI} />
      <PublicationLocationComponent customFieldsUI={customFieldsUI} />
    </>
  );
};

export { OrganizationDetailsComponent };
