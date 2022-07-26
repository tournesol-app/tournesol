import { TFunction } from 'react-i18next';
import { SUPPORTED_LANGUAGES } from 'src/i18n';
import { PollsService, Recommendation } from 'src/services/openapi';
import { OrderedDialogs } from 'src/utils/types';
import { recommendationsLanguagesFromNavigator } from 'src/utils/recommendationsLanguages';

let VIDEOS: Promise<Recommendation[]> | null = null;

/**
 * Return a list of `Recommendation` for the tutorial.
 *
 * The recommendations returned:
 *   - are safe recommendations
 *   - are in the TOP 100 of all-time recommendations...
 *     - ...having a maximum duration of 5 minutes
 *   - are filtered according to the user's navigator languages...
 *     - ...the "en" language is added if needed
 *
 * It is possible that Tournesol doesn't have any recommendation matching one
 * of the user's navigator languages.
 *
 * To prevent returning an empty list of recommendations, if the user's
 * navigator languages don't contain at least one of the languages supported
 * by the UI, the default language "en" will be added to the metadata filter
 * of the recommendations request.
 */
export function getTutorialVideos(): Promise<Recommendation[]> {
  if (VIDEOS != null) {
    return VIDEOS;
  }

  const supportedLangCodes = SUPPORTED_LANGUAGES.map((l) => l.code);
  const langIsSupported = (langCode: string) =>
    supportedLangCodes.includes(langCode);

  const metadata: Record<string, string | string[]> = {};

  const minutesMax = 5;
  const top = 100;

  metadata['duration:lte:int'] = (60 * minutesMax).toString();
  metadata['language'] = recommendationsLanguagesFromNavigator().split(',');

  // Add "en" to the recommendations request, so that users will always get
  // recommendations, even if Tournesol doesn't have any recommendation
  // matching their navigator languages.
  if (!metadata['language'].some(langIsSupported)) {
    metadata['language'].push('en');
  }

  VIDEOS = PollsService.pollsRecommendationsList({
    name: 'videos',
    metadata: metadata,
    limit: top,
  }).then((data) => data.results ?? []);
  return VIDEOS;
}

export const getTutorialDialogs = (t: TFunction): OrderedDialogs => {
  return {
    '0': {
      title: t('videos.dialogs.tutorial.title1'),
      messages: [
        t('videos.dialogs.tutorial.message1.p10'),
        t('videos.dialogs.tutorial.message1.p20'),
        t('videos.dialogs.tutorial.message1.p30'),
        t('videos.dialogs.tutorial.message1.p40'),
      ],
    },
    '1': {
      title: t('videos.dialogs.tutorial.title2'),
      messages: [
        t('videos.dialogs.tutorial.message2.p10'),
        t('videos.dialogs.tutorial.message2.p20'),
        t('videos.dialogs.tutorial.message2.p30'),
        t('videos.dialogs.tutorial.message2.p40'),
        t('videos.dialogs.tutorial.message2.p50'),
      ],
    },
    '2': {
      title: t('videos.dialogs.tutorial.title3'),
      messages: [
        t('videos.dialogs.tutorial.message3.p10'),
        t('videos.dialogs.tutorial.message3.p20'),
        t('videos.dialogs.tutorial.message3.p30'),
      ],
    },
    '3': {
      title: t('videos.dialogs.tutorial.title4'),
      messages: [
        t('videos.dialogs.tutorial.message4.p10'),
        t('videos.dialogs.tutorial.message4.p20'),
        t('videos.dialogs.tutorial.message4.p30'),
      ],
    },
  };
};
