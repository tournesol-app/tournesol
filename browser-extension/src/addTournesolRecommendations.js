(async () => {
  const { Banner } = await import(
    chrome.extension.getURL('./models/banner/Banner.js')
  );

  const { TournesolRecommendationsOptions } = await import(
    chrome.extension.getURL(
      './models/tournesolRecommendations/TournesolRecommendationsOptions.js'
    )
  );

  const { TournesolRecommendations } = await import(
    chrome.extension.getURL(
      './models/tournesolRecommendations/TournesolRecommendations.js'
    )
  );

  const { TournesolSearchRecommendations } = await import(
    chrome.extension.getURL(
      './models/tournesolRecommendations/TournesolSearchRecommendations.js'
    )
  );

  const tournesolHomeRecommendations = new TournesolRecommendations();

  const tournesolSearchRecommendationsOptions =
    new TournesolRecommendationsOptions(
      3,
      1,
      new Banner(),
      '#header-container',
      true
    );
  const tournesolSearchRecommendations = new TournesolSearchRecommendations(
    tournesolSearchRecommendationsOptions
  );

  const process = () => {
    if (location.search.includes('tournesolSearch')) {
      chrome.storage.local.set({ searchEnabled: true });
    }

    // Display the home page recommendations.
    if (location.pathname === '/') {
      tournesolHomeRecommendations.process();

    // Add results from Tournesol to the YT search results.
    } else if (location.pathname === '/results') {
      tournesolSearchRecommendations.process();
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
