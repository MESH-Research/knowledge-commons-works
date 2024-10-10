import React from "react";
import { MembersVisibilityField, VisibilityField } from "@js/invenio_communities/settings/privileges/CommunityPriviledgesForm";
import { Header } from "semantic-ui-react";
import { i18next } from "@translations/invenio_app_rdm/i18next";

const CommunityPrivilegesFormLayout = ({ formConfig, community }) => {
  return (
    <>
    <Header as="h3">
        {i18next.t("Community visibility")}
        <Header.Subheader className="mt-5">
        {i18next.t(
            "Controls if the community is visible to anyone or to members only."
        )}
        </Header.Subheader>
    </Header>
    <VisibilityField formConfig={formConfig} />

    <Header as="h3">
        {i18next.t("Members visibility")}
        <Header.Subheader className="mt-5">
        {i18next.t(
            "Controls whether the members tab is visible to anyone or to members only."
        )}
        </Header.Subheader>
    </Header>
    <MembersVisibilityField formConfig={formConfig} />
    {/* TODO: Re-enable once properly integrated to be displayed */}
    {/*
            <Grid.Column width={6}>
            <Header as="h3">Records permissions</Header>
            <p>This is a text explaining about the permission</p>
            <SelectField
                fieldPath="access.record_policy"
                options={this.props.formConfig.access.record_policy}
            />
            <Button compact primary icon labelPosition="left">
                <Icon name="save"></Icon>Save
            </Button>
            </Grid.Column>
            <Grid.Column width={10} />
            <Grid.Column width={6}>
            <Header as="h3">Members permission policy</Header>
            <p>This is a text explaining about the permission</p>
            <SelectField
                fieldPath="access.member_policy"
                options={this.props.formConfig.access.member_policy}
            />
            <Button compact primary icon labelPosition="left">
                <Icon name="save"></Icon>Save
            </Button>
            </Grid.Column>
            <Grid.Column width={10} /> */}
    </>
  );
};

export { CommunityPrivilegesFormLayout };
