// This file is part of Invenio-communities
// Copyright (C) 2022 CERN.
//
// Invenio-communities is free software; you can redistribute it and/or modify it
// under the terms of the MIT License; see LICENSE file for more details.

import { CommunityLinksExtractor } from "../CommunityLinksExtractor";
import { bulkMembersSerializer } from "../serializers";
import { http } from "react-invenio-forms";

export class CommunityInvitationsApi {
  #urls;

  constructor(community, LinksExtractor = CommunityLinksExtractor) {
    this.#urls = new LinksExtractor(community);
    this.community = community;
  }

  createInvite = async (members, role, message = undefined) => {
    const payload = {
      members: bulkMembersSerializer(members),
      role: role,
    };
    if (message) {
      payload.message = message;
    }

    return await http.post(this.#urls.invitations, payload);
  };

  addGroupToMembers = async (members, role, message = undefined) => {
    const payload = {
      members: bulkMembersSerializer(members),
      role: role,
    };
    if (message) {
      payload.message = message;
    }

    return await http.post(this.#urls.membersUrl, payload);
  };

  updateInvites = async (payload) => {
    return await http.put(this.#urls.invitations, payload);
  };

  updateRole = async (invitation, role) => {
    const memberSerialized = bulkMembersSerializer([invitation]);
    const payload = { members: memberSerialized, role: role };
    return await this.updateInvites(payload);
  };
}
