import { TournesolRecommendations } from './TournesolRecommendations.js';
import { defaultTournesolRecommendationsOptions } from './TournesolRecommendationsOptions.js';

export class TournesolSearchRecommendations extends TournesolRecommendations {
  constructor(options = defaultTournesolRecommendationsOptions) {
    super(options);
    this.searchQuery = '';
  }

  loadRecommandations() {
    if (this.areRecommendationsLoading) return;

    this.areRecommendationsLoading = true;

    chrome.storage.local.get('searchEnabled', ({ searchEnabled }) => {
      if (searchEnabled) {
        this.areRecommendationsLoading = true;
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
        //Remove the component from the previous search if the search has just been turned off
        if (this.tournesol_component) this.tournesol_component.remove();

        // reset the recommendationsLoading if search is off either it will never
        // try to reload new videos for the search
        this.areRecommendationsLoading = false;
      }
    });

    return;
  }

  process() {
    this.isPageLoaded = true;
    this.loadRecommandations();
  }

  displayRecommendations(nthchild = 0){
    super.displayRecommendations(nthchild);
  }
}
