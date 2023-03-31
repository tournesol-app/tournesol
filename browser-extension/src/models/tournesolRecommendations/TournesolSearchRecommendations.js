import { TournesolRecommendations } from './TournesolRecommendations.js';

export class TournesolSearchRecommendations extends TournesolRecommendations {
  searchQuery;

  constructor(options = defaultTournesolRecommendationsOptions) {
    super(options);
  }

  loadRecommandations() {
    // Only enable on youtube.com/results
    console.log(this);
    if (this.path != location.pathname) return;
    console.log(2);
    if (this.areRecommendationsLoading) return;
    console.log(3);
    this.areRecommendationsLoading = true;
    console.log(4);
    chrome.storage.local.get('searchEnabled', ({ searchEnabled }) => {
      console.log(5);
      if (searchEnabled) {
        console.log(6);
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
        // reset the recommendationsLoading if search is off either it will never
        // try to reload new videos for the search
        if (this.tournesol_component) this.tournesol_component.remove();
        this.areRecommendationsLoading = false;
      }
    });

    return;
  }

  process() {
    if (location.pathname === this.path) {
      this.isPageLoaded = true;
      this.loadRecommandations();
    }
  }
}
