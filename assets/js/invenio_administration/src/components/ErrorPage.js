import React, { Component } from "react";
import { Container, Header, Icon } from "semantic-ui-react";
import Overridable from "react-overridable";
import PropTypes from "prop-types";
import { i18next } from "@translations/invenio_administration/i18next";

class ErrorPage extends Component {
  render() {
    const { errorCode, errorMessage, error, children } = this.props;
    return (
      <Overridable id="Admin.ErrorPage.layout" {...this.props}>
        {error ? (
          <Container textAlign="center" className="error-handler">
            <Header as="h1" icon>
              <Icon name="warning" circular />
              {errorCode}
              <Header.Subheader>{errorMessage}</Header.Subheader>
            </Header>
          </Container>
        ) : (
          // eslint-disable-next-line react/jsx-no-useless-fragment
          <>{children}</>
        )}
      </Overridable>
    );
  }
}

ErrorPage.propTypes = {
  errorCode: PropTypes.string,
  errorMessage: PropTypes.string,
  error: PropTypes.bool,
  children: PropTypes.element,
};

ErrorPage.defaultProps = {
  errorCode: i18next.t("Error"),
  errorMessage: i18next.t("Server was not able to process your request."),
  error: false,
  children: undefined,
};

export default Overridable.component("ErrorPage", ErrorPage);
