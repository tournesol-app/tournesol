import React from 'react';
import { useLocation } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { Box } from '@mui/material';

import { ContentHeader } from 'src/components';
import { useCurrentPoll } from 'src/hooks/useCurrentPoll';
import Comparison from 'src/features/comparisons/Comparison';
import ComparisonSeries from 'src/features/comparisonSeries/ComparisonSeries';

const dialogs = {
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

const ComparisonPage = () => {
  const { t } = useTranslation();

  const location = useLocation();
  const searchParams = new URLSearchParams(location.search);
  const series: string = searchParams.get('series') || 'false';

  const { options } = useCurrentPoll();
  const tutorialLength = options?.tutorialLength ?? 0;
  const tutorialAlternatives = options?.tutorialAlternatives ?? undefined;

  return (
    <>
      <ContentHeader title={t('comparison.submitAComparison')} />
      <Box
        sx={{
          display: 'flex',
          alignItems: 'center',
          flexDirection: 'column',
          py: 2,
        }}
      >
        {series === 'true' ? (
          <ComparisonSeries
            dialogs={dialogs}
            getAlternatives={tutorialAlternatives}
            length={tutorialLength}
          />
        ) : (
          <Comparison />
        )}
      </Box>
    </>
  );
};

export default ComparisonPage;
