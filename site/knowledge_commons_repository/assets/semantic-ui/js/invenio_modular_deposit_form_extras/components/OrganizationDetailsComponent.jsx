import React from "react";
import { Segment } from "semantic-ui-react";
import { SponsoringInstitutionComponent } from "./SponsoringInstitutionComponent";
import { PublicationLocationComponent } from "@js/invenio_modular_deposit_form_extras/field_components/field_components";

const OrganizationDetailsComponent = ({ customFieldsUI }) => {
  return (
    <Segment as="fieldset" className="organization-details-fields">
      <SponsoringInstitutionComponent customFieldsUI={customFieldsUI} />
      <PublicationLocationComponent customFieldsUI={customFieldsUI} />
    </Segment>
  );
};

export { OrganizationDetailsComponent };
