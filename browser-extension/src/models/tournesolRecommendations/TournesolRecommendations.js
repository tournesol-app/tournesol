import { defaultTournesolRecommendationsOptions } from './TournesolRecommendationsOptions.js';
import { TournesolContainer } from '../tournesolContainer/TournesolContainer.js';

export class TournesolRecommendations {
  constructor(options = defaultTournesolRecommendationsOptions) {
    this.isPageLoaded = false;
    this.isExpanded = false;
    this.areRecommendationsLoading = false;
    this.areRecommendationsLoaded = false;
    this.videos = [];
    this.additionalVideos = [];
    this.recommendationsLanguage = 'en,fr';

    this.tournesolContainer = new TournesolContainer(this, options.banner);

    this.videosPerRow = options.videosPerRow;
    this.rowsWhenExpanded = options.rowsWhenExpanded;
    this.parentComponentQuery = options.parentComponentQuery;
    this.displayCriteria = options.displayCriteria;

    this.handleResponse = this.handleResponse.bind(this);
    this.displayRecommendations = this.displayRecommendations.bind(this);
  }

  getParentComponent(nthchild) {
    try {
      const parent = document.querySelector(this.parentComponentQuery);

      if (!parent || !parent.children[nthchild]) return;

      return parent;
    } catch (error) {
      return;
    }
  }

  // This part creates video boxes from API's response JSON
  displayRecommendations(nthchild = 1) {
    if (!this.videos || this.videos.length === 0) {
      // remove the component if we did not receive video from the response
      // so it remove the videos from the previous results
      if (this.tournesolHTMLElement) this.tournesolHTMLElement.remove();
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
      if (this.tournesolHTMLElement) this.tournesolHTMLElement.remove();

      // Get the container on Youtube home page in which we will insert Tournesol's component
      const container = this.getParentComponent(nthchild);

      if (!container) return;
      window.clearInterval(timer);

      // Generate component to display on Youtube home page

      this.tournesolHTMLElement = this.tournesolContainer.createHTMLElement();
      container.insertBefore(
        this.tournesolHTMLElement,
        container.children[nthchild]
      );
    }, 300);
  }

  handleResponse({
    data: videosResponse,
    recommandationsLanguages: languagesString = 'en,fr',
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
