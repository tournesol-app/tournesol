import {
  BlankEnum,
  Recommendations_defaultDateEnum,
  TournesolUserSettings,
  VideosPollUserSettings,
} from 'src/services/openapi';
import { SelectablePoll, TournesolUserSettingsKeys } from './types';
import { YOUTUBE_POLL_NAME } from './constants';

/**
 * Cast the value of the setting recommendations__default_unsafe to a value
 * expected by the recommendations' search filter 'safe/usafe'.
 */
const recoDefaultUnsafeToSearchFilter = (setting: boolean): string => {
  if (setting) {
    return 'true';
  }
  return '';
};

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

export const buildVideosDefaultRecoSearchParams = (
  searchParams: URLSearchParams,
  userSettings: VideosPollUserSettings | undefined
) => {
  if (userSettings?.recommendations__default_unsafe != undefined) {
    searchParams.set(
      'unsafe',
      recoDefaultUnsafeToSearchFilter(
        userSettings.recommendations__default_unsafe
      )
    );
  }

  if (userSettings?.recommendations__default_date != undefined) {
    searchParams.set(
      'date',
      recoDefaultDateToSearchFilter(userSettings.recommendations__default_date)
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

  const userPollSettings =
    userSettings?.[pollName as TournesolUserSettingsKeys];

  if (pollName === YOUTUBE_POLL_NAME) {
    buildVideosDefaultRecoSearchParams(searchParams, userPollSettings);
  }

  const strSearchParams = searchParams.toString();
  return searchParams ? '?' + strSearchParams : '';
};
