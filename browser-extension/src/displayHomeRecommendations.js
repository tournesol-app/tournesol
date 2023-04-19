(async () => {
  const { TournesolRecommendations } = await import(
    chrome.extension.getURL(
      './models/tournesolRecommendations/TournesolRecommendations.js'
    )
  );

  const tournesolHomeRecommendations = new TournesolRecommendations();

  const process = () => {
    if (location.search.includes('tournesolSearch')) {
      chrome.storage.local.set({ searchEnabled: true });
    }

    // Display the home page recommendations.
    if (location.pathname === '/') {
      tournesolHomeRecommendations.process();
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