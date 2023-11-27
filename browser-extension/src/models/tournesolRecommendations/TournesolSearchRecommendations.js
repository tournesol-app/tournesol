import { TournesolRecommendations } from './TournesolRecommendations.js';

export class TournesolSearchRecommendations extends TournesolRecommendations {
  constructor(options) {
    super(options);
    this.searchQuery = '';
  }

  process() {
    this.isPageLoaded = true;
    this.loadRecommandations();
  }

  displayRecommendations(nthchild = 0) {
    super.displayRecommendations(nthchild);
  }

  loadRecommandations() {
    if (this.areRecommendationsLoading) return;

    this.areRecommendationsLoading = true;
    if (this.tournesolHTMLElement) this.tournesolHTMLElement.remove();

    chrome.runtime.sendMessage(
      {
        message: 'getTournesolSearchRecommendations',
        search: this.refreshSearchQuery(),
        videosNumber: this.videosPerRow,
        additionalVideosNumber: this.videosPerRow * (this.rowsWhenExpanded - 1),
      },
      this.handleResponse
    );

    return;
  }

  refreshSearchQuery() {
    this.searchQuery = new URLSearchParams(location.search).get('search_query');
    return this.searchQuery;
  }
}
