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

  const PARENT_CSS_SELECTORS = '#page-manager #container #primary';

  const options = new TournesolRecommendationsOptions(
    3,
    1,
    new Banner(),
    PARENT_CSS_SELECTORS,
    true
  );

  const searchRecommendations = new TournesolSearchRecommendations(options);

  // Allow to display the Tournesol search results without modifying the
  // user's preferences in the local storage.
  let forceSearch = false;

  /**
   * The pre-processing of the content script.
   *
   * The code here is designed to be executed as soon as possible, before the
   * YouTube page has been loaded.
   */
  const preProcess = () => {
    const searchParams = new URLSearchParams(location.search);
    const tournesolSearch = searchParams.get('tournesolSearch') ?? '0';

    if (tournesolSearch === '1') {
      forceSearch = true;
    }
  };

  /**
   * The main process of the content script.
   *
   * Should be run after the YouTube page has been loaded.
   */
  const process = () => {
    if (location.pathname === '/results') {
      searchRecommendations.process(forceSearch);
    }
  };

  preProcess();

  document.addEventListener('yt-navigate-finish', process);

  if (document.body) {
    process();
  } else {
    document.addEventListener('DOMContentLoaded', process);
  }
})();
