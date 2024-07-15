import React from "react";
import {
  MultipleOptionsSearchBarRSK,
} from "@js/invenio_search_ui/components";
import {i18next} from "@translations/invenio_app_rdm/i18next";
import { RecordSearchBarElement } from "./RecordSearchBarElement";
import _isEmpty from "lodash/isEmpty";

export const RDMRecordMultipleSearchBarElement = ({ queryString, onInputChange }) => {
  const headerSearchbar = document.getElementById("header-search-bar");
  const searchbarOptions = JSON.parse(headerSearchbar.dataset.options);

  if (!_isEmpty(searchbarOptions) && searchbarOptions.length > 1) {
    return (
      <MultipleOptionsSearchBarRSK
        options={searchbarOptions}
        onInputChange={onInputChange}
        queryString={queryString}
        placeholder={i18next.t("Search works...")}
      />
    );
  } else {
    return (
      <RecordSearchBarElement
        onInputChange={onInputChange}
        queryString={queryString}
        placeholder={i18next.t("Search works...")}
      />
    );
  }
};