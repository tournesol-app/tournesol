(async () => {
  let searchRecommendations;

  const initializeSearchRecommendations = async () => {
    const [
      { TournesolRecommendationsOptions },
      { TournesolSearchRecommendations },
      { fetchBanner },
    ] = await Promise.all(
      [
        './models/tournesolRecommendations/TournesolRecommendationsOptions.js',
        './models/tournesolRecommendations/TournesolSearchRecommendations.js',
        './models/banner/fetchBanner.js',
      ].map((path) => import(chrome.runtime.getURL(path)))
    );

    const PARENT_CSS_SELECTORS = '#page-manager #container #primary';

    const banner = await fetchBanner();

    const options = new TournesolRecommendationsOptions({
      videosPerRow: 3,
      rowsWhenExpanded: 1,
      banner,
      parentComponentQuery: PARENT_CSS_SELECTORS,
      displayCriteria: true,
    });

    return new TournesolSearchRecommendations(options);
  };

  const processSearchRecommendations = async () => {
    if (searchRecommendations === undefined) {
      searchRecommendations = initializeSearchRecommendations();
    }
    (await searchRecommendations).process();
  };

  const clearSearchRecommendations = async () => {
    if (searchRecommendations === undefined) {
      return;
    }
    (await searchRecommendations).clear();
  };

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
            processSearchRecommendations();
          } else {
            clearSearchRecommendations();
          }
        }
      );
    } else {
      clearSearchRecommendations();
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
