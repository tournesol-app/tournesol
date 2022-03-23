import { EntitiesService, Entity, TypeEnum } from 'src/services/openapi';
import { OrderedDialogs } from 'src/utils/types';

export async function getAllCandidates(): Promise<Array<Entity>> {
  const candidates = await EntitiesService.entitiesList({
    type: TypeEnum.CANDIDATE_FR_2022,
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
  '4': {
    title: 'Commment ça fonctionne ? (1/2)',
    messages: [
      'Contrairement au système de vote classique en France, ici vous donnez ' +
        ' votre avis sur une multitudes de candidat.es.',
      "Ainsi il est possible d'exprimer son choix préféré, puis son second," +
        ' puis son troisième, etc.',
    ],
  },
  '5': {
    title: 'Commment ça fonctionne ? (2/2)',
    messages: [
      "C'est en aggrégeant les comparaisons de tous les utilisateurs que" +
        ' Tournesol est capable de comprendre leurs préférences, et de' +
        ' déterminer quel candidat.e devrait-être président.e.',
      "Ce n'est donc pas la personne qui reçoit le plus de vote qui gagne " +
        ' mais celle dont la somme des avis est la plus favorable.',
    ],
  },
  '6': {
    title: 'Merci beaucoup !',
    messages: [
      'Encore une dernière comparaison et vous pourrez voir vos résultats.',
      'Nous espérons sincèrement que vous avez apprécié cette nouvelle manière' +
        ' de voter.',
    ],
  },
};
