import { APIRoutes } from "./routes";
import { http } from "react-invenio-forms";

const getFeatured = async (apiEndpoint) => {
  return await http.get(apiEndpoint);
};

const deleteCommunity = async (community, payload) => {
  const reason = payload["removal_reason"];
  payload["removal_reason"] = { id: reason };
  // WARNING: Axios does not accept payload without data key
  return await http.delete(APIRoutes.delete(community), {
    data: { ...payload },
    headers: { ...http.headers, if_match: community.revision_id },
  });
};

const restore = async (record) => {
  return await http.post(APIRoutes.restore(record));
};

export const InvenioAdministrationCommunitiesApi = {
  getFeatured: getFeatured,
  delete: deleteCommunity,
  restore: restore,
};
