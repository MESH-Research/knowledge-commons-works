import Edit from "./Edit";
import Delete from "./Delete";
import { DeleteModalTrigger } from "./DeleteModalTrigger";
import React, { Component } from "react";
import PropTypes from "prop-types";
import isEmpty from "lodash/isEmpty";
import { ResourceActions } from "./ResourceActions";
import { Button, Dropdown } from "semantic-ui-react";
import { i18next } from "@translations/invenio_administration/i18next";
import _get from "lodash/get";

export class Actions extends Component {
  render() {
    const {
      title,
      resourceName,
      actions,
      resource,
      successCallback,
      idKeyPath,
      editUrl,
      displayEdit,
      displayDelete,
    } = this.props;

    // if number of actions is greater than 3, we display all in a dropdown
    const displayAsDropdown =
      displayEdit && displayDelete && Object.keys(actions).length > 1;

    if (displayAsDropdown) {
      return (
        <Dropdown>
          {!isEmpty(actions) && (
            <ResourceActions
              resource={resource}
              successCallback={successCallback}
              idKeyPath={idKeyPath}
              actions={actions}
              Element={Dropdown.Item}
              trigger={
                <Button
                  icon="cog"
                  size="tiny"
                  className="transparent rel-ml-1"
                  aria-label={i18next.t("Open list of actions")}
                />
              }
            />
          )}
          {displayEdit && <Edit editUrl={editUrl} resource={resource} />}
          {displayDelete && (
            <DeleteModalTrigger
              title={title}
              resourceName={resourceName}
              apiEndpoint={_get(resource, "links.self")}
              resource={resource}
              successCallback={successCallback}
              idKeyPath={idKeyPath}
              Element={Dropdown.Item}
            />
          )}
        </Dropdown>
      );
    } else {
      return (
        <Button.Group size="tiny" className="relaxed">
          {!isEmpty(actions) && (
            <ResourceActions
              resource={resource}
              successCallback={successCallback}
              idKeyPath={idKeyPath}
              actions={actions}
            />
          )}
          {displayEdit && <Edit editUrl={editUrl} resource={resource} />}
          {displayDelete && (
            <Delete
              successCallback={successCallback}
              resource={resource}
              resourceName={resourceName}
              title={title}
            />
          )}
        </Button.Group>
      );
    }
  }
}

Actions.propTypes = {
  title: PropTypes.string.isRequired,
  resourceName: PropTypes.string.isRequired,
  displayEdit: PropTypes.bool,
  displayDelete: PropTypes.bool,
  resource: PropTypes.object.isRequired,
  successCallback: PropTypes.func.isRequired,
  idKeyPath: PropTypes.string,
  actions: PropTypes.object.isRequired,
  editUrl: PropTypes.string.isRequired,
};

Actions.defaultProps = {
  displayEdit: true,
  displayDelete: true,
  idKeyPath: "pid",
};
