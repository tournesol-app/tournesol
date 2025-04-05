export class TournesolRecommendationsOptions {
  constructor({
    videosPerRow,
    rowsWhenCollapsed = 1,
    rowsWhenExpanded,
    banner,
    parentComponentQuery,
    displayCriteria,
  }) {
    this.videosPerRow = videosPerRow;
    this.rowsWhenCollapsed = rowsWhenCollapsed;
    this.rowsWhenExpanded = rowsWhenExpanded;
    this.banner = banner;
    this.parentComponentQuery = parentComponentQuery;
    this.displayCriteria = displayCriteria;
  }
}
