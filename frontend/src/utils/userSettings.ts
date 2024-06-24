import {
  BlankEnum,
  FeedForyou_dateEnum,
  Notifications_langEnum,
  Recommendations_defaultDateEnum,
  TournesolUserSettings,
  VideosPollUserSettings,
} from 'src/services/openapi';

import { YOUTUBE_POLL_NAME } from './constants';
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
  userSettings: VideosPollUserSettings | undefined
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
  }
};

export const getFeedForYouDefaultSearchParams = (
  pollName: string,
  pollOptions: SelectablePoll | undefined,
  userSettings: TournesolUserSettings
): URLSearchParams => {
  const searchParams = new URLSearchParams(
    pollOptions?.defaultFiltersFeedForYou
  );

  const userPollSettings = userSettings?.[pollName as PollUserSettingsKeys];

  if (pollName === YOUTUBE_POLL_NAME) {
    buildVideosFeedForYouSearchParams(searchParams, userPollSettings);
  }

  return searchParams;
};

export const buildVideosFeedTopItemsSearchParams = (
  searchParams: URLSearchParams,
  userSettings: VideosPollUserSettings | undefined
) => {
  if (userSettings?.feed_topitems__languages != undefined) {
    searchParams.set(
      'language',
      settingLanguagesToSearchFilter(userSettings.feed_topitems__languages)
    );
  }
};

export const getFeedTopItemsDefaultSearchParams = (
  pollName: string,
  pollOptions: SelectablePoll | undefined,
  userSettings: TournesolUserSettings
) => {
  const searchParams = new URLSearchParams(
    pollOptions?.defaultFiltersFeedTopItems
  );

  const userPollSettings = userSettings?.[pollName as PollUserSettingsKeys];

  if (pollName === YOUTUBE_POLL_NAME) {
    buildVideosFeedTopItemsSearchParams(searchParams, userPollSettings);
  }

  const strSearchParams = searchParams.toString();
  return searchParams ? '?' + strSearchParams : '';
};

export const buildVideosDefaultRecoSearchParams = (
  searchParams: URLSearchParams,
  userSettings: VideosPollUserSettings | undefined
) => {
  const advancedFilters: string[] = [];
  if (userSettings?.recommendations__default_unsafe) {
    advancedFilters.push('unsafe');
  }
  if (userSettings?.recommendations__default_exclude_compared_entities) {
    advancedFilters.push('exclude_compared');
  }
  if (advancedFilters.length > 0) {
    searchParams.set('advanced', advancedFilters.join(','));
  }

  if (userSettings?.recommendations__default_date != undefined) {
    searchParams.set(
      'date',
      settingDateToSearchFilter(userSettings.recommendations__default_date)
    );
  }

  if (userSettings?.recommendations__default_languages != undefined) {
    searchParams.set(
      'language',
      settingLanguagesToSearchFilter(
        userSettings.recommendations__default_languages
      )
    );
  }
};

export const getDefaultRecommendationsSearchParams = (
  pollName: string,
  pollOptions: SelectablePoll | undefined,
  userSettings: TournesolUserSettings
) => {
  const searchParams = new URLSearchParams(
    pollOptions?.defaultRecoSearchParams
  );

  const userPollSettings = userSettings?.[pollName as PollUserSettingsKeys];

  if (pollName === YOUTUBE_POLL_NAME) {
    buildVideosDefaultRecoSearchParams(searchParams, userPollSettings);
  }

  const strSearchParams = searchParams.toString();
  return searchParams ? '?' + strSearchParams : '';
};
