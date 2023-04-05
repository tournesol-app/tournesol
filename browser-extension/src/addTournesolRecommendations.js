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
      '#header-container'
    );
  const tournesolSearchRecommendations = new TournesolSearchRecommendations(
    tournesolSearchRecommendationsOptions
  );

  const process = () => {
    if (location.pathname === '/') tournesolHomeRecommendations.process();
    if (location.pathname === '/results')
      tournesolSearchRecommendations.process();
  };

  // Youtube doesnt completely load a video page, so content script doesn't lauch correctly without these events

  // This part is called on connection for the first time on youtube.com/*
  /* ********************************************************************* */

  document.addEventListener('yt-navigate-finish', process);
  if (document.body) process();
  else document.addEventListener('DOMContentLoaded', process);
})();
