(async () => {
  const { TournesolRecommendations } = await import(
    chrome.runtime.getURL(
      './models/tournesolRecommendations/TournesolRecommendations.js'
    )
  );

  const homeRecommendations = new TournesolRecommendations();

  const process = () => {
    // Display the home page recommendations.
    if (location.pathname === '/') {
      homeRecommendations.process();
    } else {
      homeRecommendations.clear();
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
