/*
 * This file is part of Invenio.
 * Copyright (C) 2016-2018 CERN.
 * Copyright (C) 2016 TIND.
 *
 * Invenio is free software; you can redistribute it and/or modify it
 * under the terms of the MIT License; see LICENSE file for more details.
 */

import * as $ from "jquery/dist/jquery";

$(document).ready(function() {
  $("#lang-code").on("change", function() {
    $("#language-code-form").submit();
  });
});
