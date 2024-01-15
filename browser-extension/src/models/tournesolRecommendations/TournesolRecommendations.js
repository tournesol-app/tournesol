import { TournesolContainer } from '../tournesolContainer/TournesolContainer.js';

export class TournesolRecommendations {
  constructor(options) {
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

    // The value of the query parameter `bundle` of the API /recommendations/.
    // Vary this paramater from a request to another to avoid fetching the
    // same cached recommendation results.
    this.queryParamBundle = this.initializeQueryParamBundle();
  }

  getRandomInt(max) {
    return Math.floor(Math.random() * max);
  }

  /**
   * Initialize `queryParamBundle` with a random number.
   *
   * A random number prevents the users from seeing the same cached
   * recommendation results each time they refresh the YT page. Be careful,
   * increasing the range of generated numbers will also increase the
   * theoretical maximum number of cached results by the API.
   *
   * 20 means if 1000 users press F5 at the same time, at most 40 results will
   * be cached (20 for recent reco. and 20 for older reco.).
   */
  initializeQueryParamBundle() {
    return this.getRandomInt(20);
  }

  varyQueryParamBundle() {
    this.queryParamBundle += 1 + this.getRandomInt(2);
    return this.queryParamBundle;
  }

  /**
   * Return the HTMLElement in which the recommendations will be displayed.
   *
   * Note: should this method be part of the TournesolContainer class intead?
   */
  getParentContainer(nthchild) {
    try {
      const parent = document.querySelector(this.parentComponentQuery);

      if (!parent || !parent.children[nthchild]) return;

      return parent;
    } catch (error) {
      return;
    }
  }

  /**
   * Note: should this method be part of the TournesolContainer class intead?
   */
  displayRecommendations(nthchild = 1) {
    if (!this.videos || this.videos.length === 0) {
      /**
       * When the API returns no video, remove the Tournesol container to
       * not keep on the screen the results of the previous request.
       */
      if (this.tournesolHTMLElement) this.tournesolHTMLElement.remove();
      return;
    }

    /**
     * Wait for the targetted parent container to be available.
     *
     * It seems like several HTML elements are dynamically created with
     * javascript, so running this method at document_idle in the manifest
     * doesn't work.
     */
    var timer = window.setInterval(() => {
      if (this.tournesolHTMLElement) this.tournesolHTMLElement.remove();

      // Continue if the parent has not been found...
      const parentContainer = this.getParentContainer(nthchild);
      if (!parentContainer) return;

      window.clearInterval(timer);

      // Create the Tournesol container.
      this.tournesolContainer.removeExistingContainers();
      this.tournesolHTMLElement = this.tournesolContainer.createHTMLElement();

      parentContainer.insertBefore(
        this.tournesolHTMLElement,
        parentContainer.children[nthchild]
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
        queryParamBundle: this.varyQueryParamBundle(),
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

  clear() {
    if (this.tournesolHTMLElement) this.tournesolHTMLElement.remove();
  }
}
