
import { i18next } from "@translations/invenio_communities/i18next";
import PropTypes from "prop-types";
import React, { useState } from "react";
import { withState } from "react-searchkit";
import { Input } from "semantic-ui-react";

export const RecordSearchBarElement = withState(
  ({
    placeholder: passedPlaceholder,
    queryString,
    // onInputChange,
    updateQueryState,
    currentQueryState,
    uiProps
  }) => {
    const placeholder = passedPlaceholder || i18next.t("Search");
    const [currentValue, setCurrentValue] = useState(queryString || currentQueryState.queryString || "");

    const onInputChange = (value) => {
      setCurrentValue(value);
    };

    const onSearch = () => {
      updateQueryState({ ...currentQueryState, queryString: currentValue });
    };

    const onBtnSearchClick = () => {
      onSearch();
    };
    const onKeyPress = (event) => {
      if (event.key === "Enter") {
        onSearch();
      }
    };

    return (
      <Input
        action={{
          "icon": "search",
          "onClick": onBtnSearchClick,
          "className": "search",
          "aria-label": i18next.t("Search"),
        }}
        fluid
        placeholder={placeholder}
        onChange={(event, { value }) => {
          onInputChange(value);
        }}
        value={currentValue}
        onKeyPress={onKeyPress}
        {...uiProps}
      />
    );
  }
);

RecordSearchBarElement.propTypes = {
  placeholder: PropTypes.string,
  queryString: PropTypes.string,
  onInputChange: PropTypes.func,
  updateQueryState: PropTypes.func,
  currentQueryState: PropTypes.object,
};
