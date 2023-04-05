import React, { useContext } from "react";
import { SearchBar as SKSearchBar, Sort } from "react-searchkit";
import { SearchConfigurationContext } from "@js/invenio_search_ui/components";
import { i18next } from "@translations/invenio_administration/i18next";

export const SearchBar = (props) => {
  const { sortOptions, sortOrderDisabled } = useContext(SearchConfigurationContext);
  return (
    <div className="auto-column-grid rel-mt-3">
      <SKSearchBar />
      {sortOptions && (
        <Sort
          sortOrderDisabled={sortOrderDisabled}
          values={sortOptions}
          ariaLabel={i18next.t("Sort")}
          label={(cmp) => <>{cmp}</>} // eslint-disable-line react/jsx-no-useless-fragment
        />
      )}
    </div>
  );
};

export default SearchBar;
