/*
 * This file is part of Invenio.
 * Copyright (C) 2016-2024 CERN.
 * Copyright (C) 2024      KTH Royal Institute of Technology.
 *
 * Invenio is free software; you can redistribute it and/or modify it
 * under the terms of the MIT License; see LICENSE file for more details.
 */
import React from "react";
import ReactDOM from "react-dom";
import { OverridableContext, overrideStore } from "react-overridable";
import CommunitiesCarousel from "./CommunitiesCarousel";

const communitiesCarouselContainer = document.getElementById("communities-carousel");
const title = communitiesCarouselContainer.dataset.title;
const fetchUrl = communitiesCarouselContainer.dataset.fetchUrl;
const intervalDelay = parseInt(communitiesCarouselContainer.dataset.intervalDelay);
const animationSpeed = parseInt(communitiesCarouselContainer.dataset.animationSpeed);
const defaultLogo = communitiesCarouselContainer.dataset.defaultLogo;
const itemsPerPage = communitiesCarouselContainer.dataset.itemsPerPage;
const showUploadBtn = JSON.parse(communitiesCarouselContainer.dataset.showUploadBtn);

const overriddenComponents = overrideStore.getAll();

ReactDOM.render(
  <OverridableContext.Provider value={overriddenComponents}>
    <CommunitiesCarousel
      title={title}
      fetchUrl={fetchUrl}
      intervalDelay={intervalDelay}
      animationSpeed={animationSpeed}
      defaultLogo={defaultLogo}
      itemsPerPage={itemsPerPage}
      showUploadBtn={showUploadBtn}
    />
  </OverridableContext.Provider>,
  communitiesCarouselContainer
);
