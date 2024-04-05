import { generatePath } from "react-router-dom";

const CommunitiesRoutesBase = "/collections";

export const InvenioCommunitiesRoutesList = {
  home: CommunitiesRoutesBase,
  newCommunity: `${CommunitiesRoutesBase}/new`,
  membersList: `${CommunitiesRoutesBase}/:communityId/members`,
};

export const InvenioCommunitiesRoutesGenerator = {
  membersList: (communityId) =>
    generatePath(InvenioCommunitiesRoutesList.membersList, {
      communityId: communityId,
    }),
};
