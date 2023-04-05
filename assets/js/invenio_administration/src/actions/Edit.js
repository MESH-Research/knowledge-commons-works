import PropTypes from "prop-types";
import React, { Component } from "react";
import { i18next } from "@translations/invenio_administration/i18next";
import { Button, Popup, Icon } from "semantic-ui-react";
import Overridable from "react-overridable";

class EditCmp extends Component {
  render() {
    const { display, editUrl, disable, disabledMessage, resource } = this.props;
    if (!display) {
      return null;
    }
    const disabled = disable(resource);

    return (
      <Popup
        content={disabledMessage}
        disabled={!disabled}
        trigger={
          <span className="mr-5">
            <Button as="a" disabled={disabled} href={editUrl} icon labelPosition="left">
              <Icon name="pencil" />
              {i18next.t("Edit")}
            </Button>
          </span>
        }
      />
    );
  }
}

EditCmp.propTypes = {
  display: PropTypes.bool,
  editUrl: PropTypes.string.isRequired,
  disable: PropTypes.func,
  disabledMessage: PropTypes.string,
  resource: PropTypes.object,
};

EditCmp.defaultProps = {
  display: true,
  disable: () => false,
  disabledMessage: i18next.t("Resource is not editable."),
  resource: undefined,
};

export default Overridable.component("InvenioAdministration.EditAction", EditCmp);
