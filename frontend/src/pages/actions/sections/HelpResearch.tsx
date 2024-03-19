import React from 'react';
import { Trans, useTranslation } from 'react-i18next';

import { Alert, AlertTitle, Box, Link, Typography } from '@mui/material';

const HelpResearchSection = () => {
  const { t } = useTranslation();
  return (
    <Box>
      <Typography
        variant="h4"
        fontStyle="italic"
        gutterBottom
        id="account-terms"
      >
        Aider la recherche scientifique qui est au service de la société :
      </Typography>
      <ul>
        <li>
          <Typography paragraph>
            Signer la pétition pour une recherche publique au service de la
            société.
          </Typography>
        </li>
        <li>
          <Typography paragraph>
            Promouvoir et participer au projet Tournesol, The personalization
            project, Horus, Politoscope, Their.tube…
          </Typography>
        </li>
        <li>
          <Typography paragraph>
            Assister aux Tournesol Talks, ou demander à intervenir.
          </Typography>
        </li>
      </ul>
    </Box>
  );
};

export default HelpResearchSection;
