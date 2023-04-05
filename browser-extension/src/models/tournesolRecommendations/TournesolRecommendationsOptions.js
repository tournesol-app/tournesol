import { Banner } from '../banner/Banner.js';

export class TournesolRecommendationsOptions {
  constructor(
    videosPerRow,
    rowsWhenExpanded,
    banner,
    parentComponentQuery,
    displayCriteria
  ) {
    this.videosPerRow = videosPerRow;
    this.rowsWhenExpanded = rowsWhenExpanded;
    this.banner = banner;
    this.parentComponentQuery = parentComponentQuery;
    this.displayCriteria = displayCriteria;
  }
}

export const defaultTournesolRecommendationsOptions =
  new TournesolRecommendationsOptions(
    4,
    3,
    new Banner(),
    '#primary > ytd-rich-grid-renderer',
    false
  );
