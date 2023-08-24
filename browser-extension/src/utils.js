export const getAccessToken = async () => {
  return new Promise((resolve) => {
    chrome.storage.local.get(['access_token'], (items) => {
      resolve(items.access_token);
    });
  });
};

export const alertOnCurrentTab = async (msg) => {
  chrome.tabs.executeScript({
    code: `alert("${msg}", 'ok')`,
  });
};

export const alertUseOnLinkToYoutube = () => {
  alertOnCurrentTab('This must be used on a link to a youtube video');
};

export const alertInvalidAccessToken = () => {
  alertOnCurrentTab(
    'Your connection to Tournesol needs to be refreshed.\\n\\n' +
      'Please log in using the form below.'
  );
};

export const fetchTournesolApi = async (url, method, data) => {
  const headers = {
    Accept: 'application/json',
    'Content-Type': 'application/json',
  };
  const access_token = await getAccessToken();
  if (access_token) {
    headers['Authorization'] = `Bearer ${access_token}`;
  }

  const body = {
    credentials: 'include',
    method: method,
    mode: 'cors',
    headers: headers,
  };
  if (data) {
    body['body'] = JSON.stringify(data);
  }
  return fetch(`https://api.tournesol.app/${url}`, body)
    .then((r) => {
      if (r.status === 401 || r.status === 403) {
        // 401 Unauthorized with an access token means either
        // - the token has expired
        // - the token has been crafted
        if (r.status === 401 && access_token) {
          alertInvalidAccessToken();
        }
      }
      return r;
    })
    .catch(console.error);
};

export const addRateLater = async (video_id) => {
  const ratingStatusReponse = await fetchTournesolApi(
    'users/me/rate_later/videos/',
    'POST',
    { entity: { uid: 'yt:' + video_id } }
  );
  if (ratingStatusReponse && ratingStatusReponse.ok) {
    return {
      success: true,
      message: 'Done!',
    };
  }
  if (ratingStatusReponse && ratingStatusReponse.status === 409) {
    return {
      success: true,
      message: 'Already added.',
    };
  }
  return {
    success: false,
    message: 'Failed.',
  };
};

/**
 * Retrieve the user proof related to the given keyword from the API.
 */
export const getUserProof = async (keyword) => {
  const userProofResponse = await fetchTournesolApi(
    `users/me/proof/videos?keyword=${keyword}`,
    'GET'
  );

  if ([200, 401].includes(userProofResponse.status)) {
    const responseJson = await userProofResponse.json();

    return {
      success: userProofResponse.ok,
      status: userProofResponse.status,
      body: responseJson,
    };
  }

  return { success: false };
};

export const getUserSettings = async () => {
  const userSettingsResponse = await fetchTournesolApi(
    'users/me/settings/',
    'GET'
  );

  if ([200, 401].includes(userSettingsResponse.status)) {
    const responseJson = await userSettingsResponse.json();

    return {
      success: userSettingsResponse.ok,
      status: userSettingsResponse.status,
      body: responseJson,
    };
  }

  return { success: false };
};

/*
 ** Useful method to extract a subset from an array
 ** Copied from https://stackoverflow.com/questions/11935175/sampling-a-random-subset-from-an-array
 ** Used for adding some randomness in recommendations
 */
export const getRandomSubarray = (arr, size) => {
  var shuffled = arr.slice(0),
    i = arr.length,
    temp,
    index;
  while (i--) {
    index = Math.floor((i + 1) * Math.random());
    temp = shuffled[index];
    shuffled[index] = shuffled[i];
    shuffled[i] = temp;
  }
  return shuffled.slice(0, size);
};

export const getVideoStatistics = (videoId) => {
  return fetchTournesolApi(`videos/?video_id=${videoId}`, 'GET', {});
};

/**
 * The browser API is expected to return the language indentifier following
 * the RFC 5646.
 *
 * See: https://datatracker.ietf.org/doc/html/rfc5646#section-2.1
 */
export const isNavigatorLang = (lang) => {
  let expected = lang.toLowerCase();
  let found = window.navigator.language.toLocaleLowerCase();

  // `expected` can be the shortest ISO 639 code of a language.
  //  Example: 'fr'.
  if (found === expected) {
    return true;
  }

  // The shortest ISO 639 code can be followed by other "subtags" like the
  // region, or the variant. Example: 'fr-CA'.
  if (found.startsWith(expected + '-')) {
    return true;
  }

  return false;
};

const getObjectFromLocalStorage = async (key, default_ = null) => {
  return new Promise((resolve, reject) => {
    try {
      chrome.storage.local.get(key, (value) => {
        resolve(value[key] ?? default_);
      });
    } catch (ex) {
      reject(ex);
    }
  });
};

const getRecomendationsFallbackLanguages = () => {
  const navLang = navigator.language.split('-')[0].toLowerCase();
  return ['en', 'fr'].includes(navLang) ? [navLang] : ['en'];
};

const getRecommendationsLanguagesFromStorage = async (default_) => {
  return await getObjectFromLocalStorage(
    'recommendations__default_languages',
    default_
  );
};

const getRecommendationsLanguagesFromLegacyStorage = async () => {
  const langs = await getObjectFromLocalStorage('recommendationsLanguages');

  if (langs == null) {
    return null;
  }

  return langs.split(',');
};

/**
 * The languages are retrieved following this priority order:
 *
 *  1. user's local settings
 *  2. else, the lagacy extension storage key
 *  3. else, the navigator.language
 *  4. else, the English language code is returned
 */
const getRecommendationsLanguagesAnonymous = async () => {
  const fallbackLangs = getRecomendationsFallbackLanguages();

  const legacyLangs = await getRecommendationsLanguagesFromLegacyStorage();

  const languages = await getRecommendationsLanguagesFromStorage(
    legacyLangs ?? fallbackLangs
  );

  return languages;
};

/**
 * Try to get the user's preferred recommendations languages from the
 * Tournesol API.
 *
 * Fallback to the extension local settings if the user is not authenticated,
 * or if an error occured during the request.
 *
 * Return a list of ISO 639-1 language codes that can be used to fetch the
 * recommendations from the Tournesol API.
 */
export const getRecommendationsLanguagesAuthenticated = async () => {
  let languages;
  const settings = await getUserSettings();

  // Fallback to the storage settings in case of error.
  if (!settings || !settings.success) {
    return await getRecommendationsLanguagesAnonymous();
  }

  languages = settings.body?.videos?.recommendations__default_languages ?? null;

  if (languages == null) {
    languages = await getRecommendationsLanguagesFromLegacyStorage();
  }

  if (languages == null) {
    languages = getRecomendationsFallbackLanguages();
  }

  return languages;
};
