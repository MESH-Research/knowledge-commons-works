import React from "react";
import { Header } from "semantic-ui-react";
import { i18next } from "@translations/invenio_app_rdm/i18next";
import { ReviewPolicyField } from "@js/invenio_communities/settings/curationPolicy/CurationPolicyForm";

const CurationPolicyFormLayout = ({ formConfig, community }) => {
  return (
    <>
      <Header as="h3">
        {i18next.t("Submission review policy")}
      </Header>
      <ReviewPolicyField formConfig={formConfig} />
    </>
  );
};

export { CurationPolicyFormLayout };
