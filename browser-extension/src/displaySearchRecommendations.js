(async () => {
  const bannerUrl = chrome.runtime.getURL('./models/banner/Banner.js'),
    TournesolRecommendationsOptionsUrl = chrome.runtime.getURL(
      './models/tournesolRecommendations/TournesolRecommendationsOptions.js'
    ),
    TournesolSearchRecommendationsUrl = chrome.runtime.getURL(
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
    // When loading a page, YouTube removes the extra URL parameters. In order
    // to work this statement must be executed before the parameters are
    // removed.
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
      chrome.runtime.sendMessage(
        { message: 'get:setting:extension__search_reco' },
        (setting) => {
          if (setting?.value || forceSearch) {
            searchRecommendations.process();
          } else {
            searchRecommendations.clear();
          }
        }
      );
    } else {
      searchRecommendations.clear();
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
