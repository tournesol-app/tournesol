(async () => {
  let homeRecommendations;

  const initializeHomeRecommendations = async () => {
    const [
      { TournesolRecommendations },
      { TournesolRecommendationsOptions },
      { fetchBanner },
    ] = await Promise.all(
      [
        './models/tournesolRecommendations/TournesolRecommendations.js',
        './models/tournesolRecommendations/TournesolRecommendationsOptions.js',
        './models/banner/fetchBanner.js',
      ].map((path) => import(chrome.runtime.getURL(path)))
    );

    const banner = await fetchBanner();

    const options = new TournesolRecommendationsOptions({
      videosPerRow: 4,
      rowsWhenExpanded: 3,
      banner,
      parentComponentQuery: '#primary > ytd-rich-grid-renderer',
      displayCriteria: false,
    });
    return new TournesolRecommendations(options);
  };

  const processHomeRecommendations = async () => {
    if (homeRecommendations === undefined) {
      homeRecommendations = initializeHomeRecommendations();
    }
    (await homeRecommendations).process();
  };

  const clearHomeRecommendations = async () => {
    if (homeRecommendations === undefined) {
      return;
    }
    (await homeRecommendations).clear();
  };

  const process = () => {
    // Display the home page recommendations.
    if (location.pathname === '/') {
      processHomeRecommendations();
    } else {
      clearHomeRecommendations();
    }
  };

  /**
   * YouTube doesn't completely load a video page. The content script needs
   * these events to run correctly.
   */
  document.addEventListener('yt-navigate-finish', process);

  if (document.body) {
    process();
  } else {
    document.addEventListener('DOMContentLoaded', process);
  }
})();
