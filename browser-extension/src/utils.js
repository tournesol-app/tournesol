import { apiUrl, manifestVersion } from './config.js';

export const getAccessToken = async () => {
  return new Promise((resolve) => {
    chrome.storage.local.get(['access_token'], (items) => {
      resolve(items.access_token);
    });
  });
};

const getCurrentTab = async () => {
  const queryOptions = { active: true, lastFocusedWindow: true };
  const [tab] = await chrome.tabs.query(queryOptions);
  return tab;
};

export const alertOnCurrentTab = async (msg, tab) => {
  if (manifestVersion === 2) {
    chrome.tabs.executeScript({
      code: `alert("${msg}", 'ok')`,
    });
  } else {
    tab ??= await getCurrentTab();
    const windowAlert = (msg, btn) => {
      window.alert(msg, btn);
    };
    chrome.scripting.executeScript({
      target: { tabId: tab.id },
      func: windowAlert,
      args: [msg, 'ok'],
    });
  }
};

export const alertUseOnLinkToYoutube = (tab) => {
  alertOnCurrentTab('This must be used on a link to a youtube video', tab);
};

export const fetchTournesolApi = async (path, options = {}) => {
  const { method, data, authenticate, headers: extraHeaders } = options;

  const headers = {
    Accept: 'application/json',
    ...extraHeaders,
  };

  const fetchOptions = {
    method: method ?? 'GET',
    headers,
    credentials: 'include',
    mode: 'cors',
  };

  if (data !== undefined) {
    headers['Content-Type'] = 'application/json';
    fetchOptions.body = JSON.stringify(data);
  }

  if (authenticate === undefined || authenticate === true) {
    const access_token = await getAccessToken();
    if (access_token) {
      headers['Authorization'] = `Bearer ${access_token}`;
    }
  }

  return fetch(`${apiUrl}/${path}`, fetchOptions).catch(console.error);
};

export const addRateLater = async (video_id) => {
  const ratingStatusReponse = await fetchTournesolApi(
    'users/me/rate_later/videos/',
    { method: 'POST', data: { entity: { uid: 'yt:' + video_id } } }
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
    `users/me/proof/videos?keyword=${keyword}`
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
  const userSettingsResponse = await fetchTournesolApi('users/me/settings/');

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
  return fetchTournesolApi(`videos/?video_id=${videoId}`);
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

/**
 *
 * User preferences.
 *
 */

const LEGACY_SETTINGS_MAP = {
  extension__search_reco: 'searchEnabled',
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

const getSingleSettingAnonymous = async (name) => {
  let value = await getObjectFromLocalStorage(name);

  if (value == null && name in LEGACY_SETTINGS_MAP) {
    value = await getObjectFromLocalStorage(LEGACY_SETTINGS_MAP[name]);
  }

  return value;
};

/**
 * Get a user setting from the Tournesol API. By default, fallback to the
 * local settings for anonymous users or when an API error occured.
 *
 * @param {string} name Name of the setting.
 * @param {any} default_ The value returned if the setting is undefined.
 * @param {boolean} localFallback If false, don't return the local setting if
 *                  the user is not logged, or in case of API error.
 * @param {string} scope The scope in which the API setting is located.
 * @returns
 */
export const getSingleSetting = async (
  name,
  default_ = null,
  localFallback = true,
  scope = 'videos'
) => {
  const settings = await getUserSettings();

  // Fallback to the storage settings in case of error.
  if (!settings || !settings.success) {
    if (localFallback) {
      const local = await getSingleSettingAnonymous(name);
      return local ?? default_;
    } else {
      return default_;
    }
  }

  return settings.body?.[scope]?.[name] ?? default_;
};
