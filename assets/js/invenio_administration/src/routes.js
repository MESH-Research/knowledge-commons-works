import _get from "lodash/get";

const AdminUIRoutesGenerators = {
  detailsView: (routePrefix, resource, idKeyPath = "pid") => {
    return `${routePrefix}/${_get(resource, idKeyPath)}`;
  },
  editView: (routePrefix, resource, idKeyPath = "pid") => {
    return `${routePrefix}/${_get(resource, idKeyPath)}/edit`;
  },
};

export const AdminUIRoutes = {
  ...AdminUIRoutesGenerators,
};
