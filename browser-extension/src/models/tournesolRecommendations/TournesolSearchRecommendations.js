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

    chrome.storage.local.get('searchEnabled', ({ searchEnabled }) => {
      if (searchEnabled) {
        this.searchQuery = location.search
          .substring(1)
          .split('&')
          .reduce((cur, next) => {
            let param = next.split('=');
            if (param[0] === 'search_query') {
              return param[1];
            }
            return cur;
          }, null);

        chrome.runtime.sendMessage(
          {
            message: 'getTournesolSearchRecommendations',
            search: this.searchQuery,
            videosNumber: this.videosPerRow,
            additionalVideosNumber:
              this.videosPerRow * (this.rowsWhenExpanded - 1),
          },
          this.handleResponse
        );
      } else {
        /**
         * Remove the Tournesol container to not keep on the screen the
         * results of the previous request.
         */
        if (this.tournesolHTMLElement) this.tournesolHTMLElement.remove();
        this.areRecommendationsLoading = false;
      }
    });

    return;
  }
}
