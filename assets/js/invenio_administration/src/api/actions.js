import { APIRoutes } from "./routes";
import { http } from "react-invenio-forms";

const getResource = async (apiEndpoint, pid, requestHeaders) => {
  return await http.get(APIRoutes.get(apiEndpoint, pid), { headers: requestHeaders });
};

const deleteResource = async (apiEndpoint) => {
  return await http.delete(apiEndpoint);
};

const editResource = async (apiEndpoint, pid, payload) => {
  return await http.put(APIRoutes.get(apiEndpoint, pid), payload);
};

const createResource = async (apiEndpoint, payload) => {
  return await http.post(apiEndpoint, payload);
};

const resourceAction = async (endpoint, payload) => {
  return await http.post(endpoint, payload);
};

export const InvenioAdministrationActionsApi = {
  deleteResource: deleteResource,
  editResource: editResource,
  getResource: getResource,
  resourceAction: resourceAction,
  createResource: createResource,
};
