// This file is part of Invenio-communities
// Copyright (C) 2022 CERN.
//
// Invenio-communities is free software; you can redistribute it and/or modify it
// under the terms of the MIT License; see LICENSE file for more details.

import { http } from "react-invenio-forms";

export class UsersApi {
  get endpoint() {
    return `/api/users`;
  }

  getUsers = async (query) => {
    return await http.get(`${this.endpoint}?q=${query}`);
  };
}
