import React from 'react';
import { Trans, useTranslation } from 'react-i18next';

import { Alert, AlertTitle, Box, Link, Typography } from '@mui/material';

const HelpResearchSection = () => {
  const { t } = useTranslation();
  return (
    <Box sx={{ '& li': { mt: 1 } }}>
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
          <Typography>
            Signer la pétition pour une recherche publique au service de la
            société.
          </Typography>
        </li>
        <li>
          <Typography>
            Promouvoir et participer au projet Tournesol, The personalization
            project, Horus, Politoscope, Their.tube…
          </Typography>
        </li>
        <li>
          <Typography>
            Assister aux Tournesol Talks, ou demander à intervenir.
          </Typography>
        </li>
      </ul>
    </Box>
  );
};

export default HelpResearchSection;
