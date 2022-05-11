import { TFunction } from 'react-i18next';
import { EntitiesService, Entity, TypeEnum } from 'src/services/openapi';
import { OrderedDialogs } from 'src/utils/types';

let VIDEOS: Promise<Entity[]> | null = null;

export function getTutoFriendlyVideos(): Promise<Entity[]> {
  if (VIDEOS != null) {
    return VIDEOS;
  }
  VIDEOS = EntitiesService.entitiesList({
    type: TypeEnum.VIDEO,
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
      ],
    },
  };
};
