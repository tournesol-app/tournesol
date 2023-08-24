import {
  BlankEnum,
  Notifications_langEnum,
  Recommendations_defaultDateEnum,
  TournesolUserSettings,
  VideosPollUserSettings,
} from 'src/services/openapi';

import { YOUTUBE_POLL_NAME } from './constants';
import { SelectablePoll, PollUserSettingsKeys } from './types';

/**
 * Cast the value of the setting recommendations__default_date to a value
 * expected by the recommendations' search filter 'date'.
 */
const recoDefaultDateToSearchFilter = (
  setting: Recommendations_defaultDateEnum | BlankEnum
): string => {
  if (setting === Recommendations_defaultDateEnum.ALL_TIME) {
    return '';
  }

  return setting.charAt(0) + setting.slice(1).toLowerCase();
};

/**
 * Cast the value of the setting recommendations__default_languages to a value
 * expected by the recommendations' search filter 'language'.
 */
const recoDefaultLanguagesToSearchFilter = (setting: string[]): string => {
  return setting.join(',');
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
      recoDefaultDateToSearchFilter(userSettings.recommendations__default_date)
    );
  }

  if (userSettings?.recommendations__default_languages != undefined) {
    searchParams.set(
      'language',
      recoDefaultLanguagesToSearchFilter(
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
