import React from "react";
import PropTypes from "prop-types";
import { Pagination as PaginationComponent } from "semantic-ui-react";

export const Pagination = ({ size, page, totalLength, setPage }) => {
  const totalPages = Math.ceil(totalLength / size);

  const shouldShow = totalLength > size;

  return shouldShow ? (
    <PaginationComponent
      totalPages={totalPages}
      activePage={page}
      onPageChange={(event, { activePage }) => setPage(activePage)}
    />
  ) : null;
};

Pagination.propTypes = {
  size: PropTypes.number,
  page: PropTypes.number,
  totalLength: PropTypes.number,
  setPage: PropTypes.func.isRequired,
};

Pagination.defaultProps = {
  size: 1,
  page: 1,
  totalLength: 1,
};
