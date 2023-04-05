/*
 * This file is part of Invenio.
 * Copyright (C) 2017-2022 CERN.
 *
 * Invenio is free software; you can redistribute it and/or modify it
 * under the terms of the MIT License; see LICENSE file for more details.
 */

import { createMedia } from "@artsy/fresnel";

// IMPORTANT: align changes with site.variables
export const breakpoints = {
  void: 0,
  mobile: 320,
  tablet: 768,
  computer: 1300,
  largeScreen: 1680,
  widescreen: 1920,
};

export const AppMedia = createMedia({
  breakpoints: breakpoints,
});

