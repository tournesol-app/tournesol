import React from 'react';
import { Trans, useTranslation } from 'react-i18next';

import { Alert, AlertTitle, Box, Link, Typography } from '@mui/material';

const BeEducatedSection = () => {
  const { t } = useTranslation();
  return (
    <Box sx={{ '& li': { mt: 1 } }}>
      <Typography
        variant="h4"
        fontStyle="italic"
        gutterBottom
        id="actions-be-educated"
      >
        Être formé et former les autres aux fondamentaux de la démocratie
        numérique.
      </Typography>
      <Box my={2}>
        <Alert severity="info" icon={false}>
          Si tu es éduqué tu as un meilleur impact
        </Alert>
      </Box>
      <ul>
        <li>
          <Typography>
            Lire et offrir le livre La Dictature des Algorithmes, issu des
            travaux de l’Association Tournesol.
          </Typography>
        </li>
        <li>
          <Typography>
            Visionner et partager les contenus de Science4All, Après la Bière et
            La Fabrique Sociale, parmi d’autres.
          </Typography>
        </li>
        <li>
          <Typography>
            Écouter et recommander des podcasts comme Your Undivided Attention.
          </Typography>
        </li>
        <li>
          <Typography>
            Découvrir, consommer et diffuser les jeux de la développeuse Nicky
            Case.
          </Typography>
        </li>
      </ul>
    </Box>
  );
};

export default BeEducatedSection;
