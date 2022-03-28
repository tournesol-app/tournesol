import { TFunction } from 'react-i18next';
import { EntitiesService, Entity, TypeEnum } from 'src/services/openapi';
import { OrderedDialogs } from 'src/utils/types';

let CANDIDATES: Promise<Entity[]> | null = null;

export function getAllCandidates(): Promise<Entity[]> {
  if (CANDIDATES != null) {
    return CANDIDATES;
  }
  CANDIDATES = EntitiesService.entitiesList({
    type: TypeEnum.CANDIDATE_FR_2022,
  }).then((data) => data.results ?? []);
  return CANDIDATES;
}

export const getTutorialDialogs = (t: TFunction): OrderedDialogs => {
  return {
    '0': {
      title: t('presidentielle2022.dialogs.tutorial.title1'),
      messages: [
        t('presidentielle2022.dialogs.tutorial.message1.p10'),
        t('presidentielle2022.dialogs.tutorial.message1.p20'),
        t('presidentielle2022.dialogs.tutorial.message1.p30'),
        t('presidentielle2022.dialogs.tutorial.message1.p40'),
      ],
    },
    '1': {
      title: t('presidentielle2022.dialogs.tutorial.title2'),
      messages: [
        t('presidentielle2022.dialogs.tutorial.message2.p10'),
        t('presidentielle2022.dialogs.tutorial.message2.p20'),
      ],
    },
    '2': {
      title: t('presidentielle2022.dialogs.tutorial.title3'),
      messages: [
        t('presidentielle2022.dialogs.tutorial.message3.p10'),
        t('presidentielle2022.dialogs.tutorial.message3.p20'),
      ],
    },
    '3': {
      title: t('presidentielle2022.dialogs.tutorial.title4'),
      messages: [
        t('presidentielle2022.dialogs.tutorial.message4.p10'),
        t('presidentielle2022.dialogs.tutorial.message4.p20'),
        t('presidentielle2022.dialogs.tutorial.message4.p30'),
      ],
    },
    '4': {
      title: t('presidentielle2022.dialogs.tutorial.title5'),
      messages: [
        t('presidentielle2022.dialogs.tutorial.message5.p10'),
        t('presidentielle2022.dialogs.tutorial.message5.p20'),
      ],
    },
    '5': {
      title: t('presidentielle2022.dialogs.tutorial.title6'),
      messages: [
        t('presidentielle2022.dialogs.tutorial.message6.p10'),
        t('presidentielle2022.dialogs.tutorial.message6.p20'),
        t('presidentielle2022.dialogs.tutorial.message6.p30'),
      ],
    },
    '6': {
      title: t('presidentielle2022.dialogs.tutorial.title7'),
      messages: [
        t('presidentielle2022.dialogs.tutorial.message7.p10'),
        t('presidentielle2022.dialogs.tutorial.message7.p20'),
      ],
    },
  };
};
