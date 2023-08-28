import { TournesolRecommendations } from './TournesolRecommendations.js';
import { defaultTournesolRecommendationsOptions } from './TournesolRecommendationsOptions.js';

export class TournesolSearchRecommendations extends TournesolRecommendations {
  constructor(options = defaultTournesolRecommendationsOptions) {
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

    // set this value at the end of handleReponse
    this.areRecommendationsLoading = false;

    return;
  }

  refreshSearchQuery() {
    this.searchQuery = new URLSearchParams(location.search).get('search_query');
    return this.searchQuery;
  }
}
