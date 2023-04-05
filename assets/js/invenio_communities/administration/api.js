import { http } from "react-invenio-forms";

const getFeatured = async (apiEndpoint) => {
  return await http.get(apiEndpoint);
};

export const InvenioAdministrationCommunitiesApi = {
  getFeatured: getFeatured,
};
