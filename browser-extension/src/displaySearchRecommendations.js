(async () => {
  const bannerUrl = chrome.extension.getURL('./models/banner/Banner.js'),
    TournesolRecommendationsOptionsUrl = chrome.extension.getURL(
      './models/tournesolRecommendations/TournesolRecommendationsOptions.js'
    ),
    TournesolSearchRecommendationsUrl = chrome.extension.getURL(
      './models/tournesolRecommendations/TournesolSearchRecommendations.js'
    );

  const [
    { Banner },
    { TournesolRecommendationsOptions },
    { TournesolSearchRecommendations },
  ] = await Promise.all([
    import(bannerUrl),
    import(TournesolRecommendationsOptionsUrl),
    import(TournesolSearchRecommendationsUrl),
  ]);

  const tournesolSearchRecommendationsOptions =
    new TournesolRecommendationsOptions(
      3,
      1,
      new Banner(),
      '.style-scope.ytd-page-manager #container',
      true
    );
  const tournesolSearchRecommendations = new TournesolSearchRecommendations(
    tournesolSearchRecommendationsOptions
  );

  const process = () => {
    if (location.search.includes('tournesolSearch')) {
      chrome.storage.local.set({ searchEnabled: true });
    }
    // Add results from Tournesol to the YT search results.
    if (location.pathname === '/results') {
      tournesolSearchRecommendations.process();
    }
  };

  document.addEventListener('yt-navigate-finish', process);

  if (document.body) process();
  else document.addEventListener('DOMContentLoaded', process);
})();
