import _get from "lodash/get";

const APIRoutesGenerators = {
  detailsView: (routePrefix, resource, idKeyPath = "pid") => {
    return `${routePrefix}/${_get(resource, idKeyPath)}`;
  },
  get: (routePrefix, pid) => {
    return `${routePrefix}/${pid}`;
  },
};

export const APIRoutes = {
  ...APIRoutesGenerators,
};
