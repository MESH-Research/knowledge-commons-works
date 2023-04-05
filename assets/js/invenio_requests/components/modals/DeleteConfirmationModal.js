import React, { Component } from "react";
import BaseModal from "./BaseModal";
import { i18next } from "@translations/invenio_requests/i18next";
import PropTypes from "prop-types";
import { errorSerializer } from "../../api/serializers";

export class DeleteConfirmationModal extends Component {
  constructor(props) {
    super(props);

    this.state = {
      isLoading: false,
      error: "",
    };
  }

  onDelete = async () => {
    const { action, onClose } = this.props;

    this.setState({
      isLoading: true,
    });

    try {
      await action();
      this.setState({
        isLoading: false,
        error: "",
      });
      onClose();
    } catch (error) {
      this.setState({
        isLoading: false,
        error: errorSerializer(error),
      });
    }
  };

  render() {
    const { onOpen, onClose, open } = this.props;
    const { isLoading, error } = this.state;

    return (
      <BaseModal
        contentText={i18next.t("Are you sure you want to delete this comment?")}
        action={this.onDelete}
        open={open}
        onOpen={onOpen}
        onClose={onClose}
        isLoading={isLoading}
        error={error}
        headerText={i18next.t("Confirm")}
        cancelButtonText={i18next.t("Cancel")}
        actionButtonText={i18next.t("Delete")}
      />
    );
  }
}

DeleteConfirmationModal.propTypes = {
  open: PropTypes.bool.isRequired,
  onOpen: PropTypes.func.isRequired,
  onClose: PropTypes.func.isRequired,
};
