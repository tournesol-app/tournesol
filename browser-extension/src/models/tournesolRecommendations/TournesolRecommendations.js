import { defaultTournesolRecommendationsOptions } from './TournesolRecommendationsOptions.js';
import { TournesolComponent } from '../tournesolComponent/TournesolComponent.js';

export class TournesolRecommendations {
  constructor(options = defaultTournesolRecommendationsOptions) {
    this.isPageLoaded = false;
    this.isExpanded = false;
    this.areRecommendationsLoading = false;
    this.areRecommendationsLoaded = false;
    this.videos = [];
    this.additionalVideos = [];
    this.recommendationsLanguage = 'en';

    this.tournesolComponent = new TournesolComponent(options.banner);

    this.videosPerRow = options.videosPerRow;
    this.rowsWhenExpanded = options.rowsWhenExpanded;
    this.path = options.path;
    this.parentComponentQuery = options.parentComponentQuery;
    this.handleResponse = this.handleResponse.bind(this);
    this.displayRecommendations = this.displayRecommendations.bind(this);
  }

  getParentComponent() {
    try {
      // Get parent element for the boxes in youtube page
      let contents;

      contents = document.querySelector(this.parentComponentQuery);

      if (!contents || !contents.children[1]) return;

      return contents;
    } catch (error) {
      return;
    }
  }

  // This part creates video boxes from API's response JSON
  displayRecommendations() {
    if (!this.videos || this.videos.length === 0) {
      // remove the component if we did not receive video from the response
      // so it remove the videos from the previous results
      if (this.tournesol_component) this.tournesol_component.remove();
      return;
    }

    // Timer will run until needed elements are generated
    var timer = window.setInterval(() => {
      /*
       ** Wait for needed elements to be generated
       ** It seems those elements are generated via javascript, so run-at document_idle in manifest is not enough to prevent errors
       **
       ** Some ids on video pages are duplicated, so I take the first non-duplicated id and search in its childs the correct div to add the recommendations
       ** Note: using .children[index] when child has no id
       */
      if (this.tournesol_component) this.tournesol_component.remove();
      // Get the container on Youtube home page in which we will insert Tournesol's component
      let container = this.getParentComponent();

      if (!container) return;
      window.clearInterval(timer);

      // Generate component to display on Youtube home page

      this.tournesol_component = this.tournesolComponent.getComponent(this);
      container.insertBefore(this.tournesol_component, container.children[1]);
    }, 300);
  }

  handleResponse({
    data: videosResponse,
    recommandationsLanguages: languagesString = 'en',
  }) {
    this.areRecommendationsLoading = false;
    this.areRecommendationsLoaded = true;
    this.videos = videosResponse.slice(0, this.videosPerRow);
    this.additionalVideos = videosResponse.slice(this.videosPerRow);
    this.recommandationsLanguages = languagesString;

    if (this.isPageLoaded) {
      this.displayRecommendations();
    }
  }

  loadRecommandations() {
    // Only enable on youtube.com/
    if (location.pathname != this.path) return;

    if (this.areRecommendationsLoading) return;

    this.areRecommendationsLoading = true;

    chrome.runtime.sendMessage(
      {
        message: 'getTournesolRecommendations',
        videosNumber: this.videosPerRow,
        additionalVideosNumber: this.videosPerRow * (this.rowsWhenExpanded - 1),
      },
      this.handleResponse
    );
  }

  process() {
    this.isPageLoaded = true;

    if (location.pathname === this.path) {
      if (this.videos.length > 0) {
        this.displayRecommendations();
      } else if (!this.areRecommendationsLoaded) {
        // If the content script is loaded on a non-root URL the recommendations
        // are not loaded. So if the user then goes to the root URL and the content
        // script is not reloaded, we need to load the recommendations.
        this.loadRecommandations();
      }
    }
  }
}
