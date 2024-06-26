import {
  BlankEnum,
  FeedForyou_dateEnum,
  Notifications_langEnum,
  Recommendations_defaultDateEnum,
  TournesolUserSettings,
  VideosPollUserSettings,
} from 'src/services/openapi';

import { FEED_LANG_KEY as FEED_TOPITEMS_LANG_KEY } from 'src/pages/feed/FeedTopItems';

import { YOUTUBE_POLL_NAME } from './constants';
import {
  initRecoLanguages,
  initRecoLanguagesWithLocalStorage,
} from './recommendationsLanguages';
import { SelectablePoll, PollUserSettingsKeys } from './types';

/**
 * Cast `lang` to a value of `Notifications_langEnum` if possible, else
 * return Notifications_langEnum.EN.
 */
export const resolvedLangToNotificationsLang = (
  lang: string | undefined
): Notifications_langEnum => {
  if (!lang) {
    return Notifications_langEnum.EN;
  }

  if (
    Object.values(Notifications_langEnum)
      .map((x) => String(x))
      .includes(lang)
  ) {
    return lang as Notifications_langEnum;
  }

  return Notifications_langEnum.EN;
};

/**
 * Cast the value of the setting feed_foryou__date (or similar) to a value
 * expected by the search filter 'date'.
 */
const settingDateToSearchFilter = (
  setting: FeedForyou_dateEnum | Recommendations_defaultDateEnum | BlankEnum
): string => {
  if (setting === FeedForyou_dateEnum.ALL_TIME) {
    return '';
  }

  return setting.charAt(0) + setting.slice(1).toLowerCase();
};

/**
 * Cast the value of the setting feed_foryou__languages (or similar) to a
 * value expected by the search filter 'language'.
 */
const settingLanguagesToSearchFilter = (setting: string[]): string => {
  return setting.join(',');
};

export const buildVideosFeedForYouSearchParams = (
  searchParams: URLSearchParams,
  userSettings: VideosPollUserSettings | undefined,
  langsDiscovery = false
) => {
  const advancedFilters: string[] = [];

  if (userSettings?.feed_foryou__exclude_compared_entities) {
    advancedFilters.push('exclude_compared');
  }
  if (userSettings?.feed_foryou__unsafe) {
    advancedFilters.push('unsafe');
  }

  if (advancedFilters.length > 0) {
    searchParams.set('advanced', advancedFilters.join(','));
  }

  if (userSettings?.feed_foryou__date != undefined) {
    searchParams.set(
      'date',
      settingDateToSearchFilter(userSettings.feed_foryou__date)
    );
  }

  if (userSettings?.feed_foryou__languages != undefined) {
    searchParams.set(
      'language',
      settingLanguagesToSearchFilter(userSettings.feed_foryou__languages)
    );
  } else if (langsDiscovery) {
    searchParams.set('language', initRecoLanguages());
  }
};

export const getFeedForYouDefaultSearchParams = (
  pollName: string,
  pollOptions: SelectablePoll | undefined,
  userSettings: TournesolUserSettings,
  langsDiscovery = false
): URLSearchParams => {
  const searchParams = new URLSearchParams(
    pollOptions?.defaultFiltersFeedForYou
  );

  const userPollSettings = userSettings?.[pollName as PollUserSettingsKeys];

  if (pollName === YOUTUBE_POLL_NAME) {
    buildVideosFeedForYouSearchParams(
      searchParams,
      userPollSettings,
      langsDiscovery
    );
  }

  return searchParams;
};

export const buildVideosFeedTopItemsSearchParams = (
  pollName: string,
  searchParams: URLSearchParams,
  userSettings: VideosPollUserSettings | undefined,
  langsDiscovery = false
) => {
  if (userSettings?.feed_topitems__languages != undefined) {
    searchParams.set(
      'language',
      settingLanguagesToSearchFilter(userSettings.feed_topitems__languages)
    );
  } else if (langsDiscovery) {
    searchParams.set(
      'language',
      initRecoLanguagesWithLocalStorage(pollName, FEED_TOPITEMS_LANG_KEY)
    );
  }
};

export const getFeedTopItemsDefaultSearchParams = (
  pollName: string,
  pollOptions: SelectablePoll | undefined,
  userSettings: TournesolUserSettings,
  langsDiscovery = false
) => {
  const searchParams = new URLSearchParams(
    pollOptions?.defaultFiltersFeedTopItems
  );

  const userPollSettings = userSettings?.[pollName as PollUserSettingsKeys];

  if (pollName === YOUTUBE_POLL_NAME) {
    buildVideosFeedTopItemsSearchParams(
      pollName,
      searchParams,
      userPollSettings,
      langsDiscovery
    );
  }

  const strSearchParams = searchParams.toString();
  return searchParams ? '?' + strSearchParams : '';
};
