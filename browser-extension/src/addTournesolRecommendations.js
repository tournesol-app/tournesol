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
    // random recommendations only on youtube home page
    if (location.pathname === '/') tournesolHomeRecommendations.process();
    // search recommendations only on youtube search page
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
