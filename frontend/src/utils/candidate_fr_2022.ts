import { EntitiesService, Entity } from 'src/services/openapi';
import { OrderedDialogs } from 'src/utils/types';

export async function getAllCandidates(): Promise<Array<Entity>> {
  const candidates = await EntitiesService.entitiesList({
    type: 'candidate_fr_2022',
  });

  return candidates?.results ?? [];
}

export const tutorialDialogs: OrderedDialogs = {
  '0': {
    title: 'Bienvenue dans Tournesol',
    messages: [
      'Pour vous familiariser avec ce système de comparaison, des petits' +
        ' messages comme celui-ci apparaîtront pour vous guider pas à pas.',
      'Commençons par une première comparaison 🌻',
      'Faites coulisser la poignée bleu au dessous des candidat.es, puis' +
        " enregistrez pour indiquer qui d'après vous devrait-être président.e.",
      'Plus la poignée est au centre, plus les candidat.es sont considérés comme ' +
        'similaires.',
    ],
  },
  '1': {
    title: 'Bravo !',
    messages: [
      "Continuons avec d'autres comparaisons.",
      'Notez que vous pouvez choisir manuellement les candidat.es. en utilisant' +
        ' le menu déroulant qui se trouve au dessus de leurs photos.',
    ],
  },
  '2': {
    title: 'Un conseil',
    messages: [
      "Ne vous en faites pas trop si vous n'etes pas sûr.e de vous. Il vous" +
        ' sera possible de modifier toutes vos comparaisons par la suite.',
    ],
  },
  '3': {
    title: 'Avez-vous remarqué ?',
    messages: [
      'Il y a aussi des critères de comparaison optionnel sous les critères' +
        ' principaux',
      'Essayez de dérouler les critères optionnels pour donner un avis plus' +
        ' complet sur les candidat.es',
    ],
  },
};
