import React from "react";

export const BulkActionsContext = React.createContext({
  bulkActionContext: {},
  addToSelected: () => {},
  allSelected: false,
  setAllSelected: () => {},
  selectedCount: 0,
});
