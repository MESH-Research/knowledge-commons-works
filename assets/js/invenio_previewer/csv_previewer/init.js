/*
 * This file is part of Invenio.
 * Copyright (C) 2015-2020 CERN.
 *
 * Invenio is free software; you can redistribute it and/or modify it
 * under the terms of the MIT License; see LICENSE file for more details.
 */

import $ from "jquery";
import CSV_D3JS from "./csv_d3js";
import Loader from "./loader.js";

$(function () {
  $("[data-csv-source]").each(function () {
    CSV_D3JS.attachTo($(this));
  });
  $("[data-csv-target]").each(function () {
    Loader.attachTo($(this));
  });
});
