import React from 'react';
import { useTranslation } from 'react-i18next';

import { Box, Typography } from '@mui/material';

const Moderation = () => {
  const { t } = useTranslation();
  return (
    <Box>
      <Typography variant="h4" fontStyle="italic" gutterBottom id="moderation">
        {t('termsOfService.moderation.moderation')}
      </Typography>
      <Typography paragraph>
        {t('termsOfService.moderation.paragraphs.theTournesolAssociationWill')}
      </Typography>
      <Typography paragraph>
        {t('termsOfService.moderation.paragraphs.dependingOnTheSeverityWe')}
      </Typography>
      <ul>
        <li>
          <Typography variant="body1">
            {t('termsOfService.moderation.paragraphs.accountSuspension')}
          </Typography>
        </li>
        <li>
          <Typography variant="body1">
            {t('termsOfService.moderation.paragraphs.accountTermination')}
          </Typography>
        </li>
        <li>
          <Typography variant="body1">
            {t('termsOfService.moderation.paragraphs.removalOfAddedContents')}
          </Typography>
        </li>
      </ul>
    </Box>
  );
};

export default Moderation;
