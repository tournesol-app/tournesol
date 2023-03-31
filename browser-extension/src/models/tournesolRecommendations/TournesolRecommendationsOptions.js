import { Banner } from '../banner/Banner.js';

export class TournesolRecommendationsOptions {
  constructor(
    videosPerRow,
    rowsWhenExpanded,
    path,
    banner,
    parentComponentQuery
  ) {
    this.videosPerRow = videosPerRow;
    this.rowsWhenExpanded = rowsWhenExpanded;
    this.path = path;
    this.banner = banner;
    this.parentComponentQuery = parentComponentQuery;
  }
}

export const defaultTournesolRecommendationsOptions =
  new TournesolRecommendationsOptions(
    4,
    3,
    '/',
    new Banner(),
    '#primary > ytd-rich-grid-renderer'
  );
