import React from 'react';
import { TFunction } from 'react-i18next';

import { Button, Link } from '@mui/material';

import { SUPPORTED_LANGUAGES } from 'src/i18n';
import { PollsService, Recommendation } from 'src/services/openapi';
import { recommendationsLanguagesFromNavigator } from 'src/utils/recommendationsLanguages';
import { OrderedDialogs, OrderedTips } from 'src/utils/types';

import { getWebExtensionUrl } from '../extension';

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

export const getTutorialDialogActions = (
  t: TFunction
): { [key: string]: { action: React.ReactNode } } => {
  return {
    '3': {
      action: (
        <Button
          color="secondary"
          variant="outlined"
          component={Link}
          href={getWebExtensionUrl()}
          target="_blank"
          rel="noreferrer"
        >
          {t('videos.dialogs.tutorial.installTheExtension')}
        </Button>
      ),
    },
  };
};

export const getTutorialDialogs = (t: TFunction): OrderedDialogs => {
  return {
    '3': {
      title: t('videos.dialogs.tutorial.title4'),
      messages: [
        t('videos.dialogs.tutorial.message4.p10'),
        t('videos.dialogs.tutorial.message4.p20'),
      ],
      mobile: false,
    },
  };
};

export const getTutorialTips = (t: TFunction): OrderedTips => {
  return {
    '0': {
      title: t('videos.tips.tutorial.title1'),
      messages: [
        t('videos.tips.tutorial.message1.p10'),
        t('videos.tips.tutorial.message1.p20'),
      ],
    },
    '1': {
      title: t('videos.tips.tutorial.title2'),
      messages: [
        t('videos.tips.tutorial.message2.p10'),
        t('videos.tips.tutorial.message2.p20'),
      ],
    },
    '2': {
      title: t('videos.tips.tutorial.title3'),
      messages: [
        t('videos.tips.tutorial.message3.p10'),
        t('videos.tips.tutorial.message3.p20'),
      ],
    },
    '3': {
      title: t('videos.tips.tutorial.title4'),
      messages: [
        t('videos.tips.tutorial.message4.p10'),
        t('videos.tips.tutorial.message4.p20'),
        t('videos.tips.tutorial.message4.p30'),
      ],
    },
  };
};
