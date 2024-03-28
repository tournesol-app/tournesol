import React from 'react';
import { Trans, useTranslation } from 'react-i18next';

import { Box, Typography } from '@mui/material';

import { ExternalLink } from 'src/components';

const OrientYourCareer = () => {
  const { t } = useTranslation();
  return (
    <Box>
      <Typography
        variant="h4"
        fontStyle="italic"
        gutterBottom
        id="orient-your-career"
      >
        {t('actionsPage.orientYourCareer.orientYourCareerToImprove')}
      </Typography>
      <ul>
        <li>
          <Typography>
            <Trans
              t={t}
              i18nKey="actionsPage.orientYourCareer.questionYourCareerPath"
            >
              Question your career path and consider alternatives. Read, for
              instance, the article{' '}
              <ExternalLink href="https://waitbutwhy.com/2018/04/picking-career.html">
                How to pick a career (that actually fits you)
              </ExternalLink>
              .
            </Trans>
          </Typography>
        </li>
        <li>
          <Typography>
            {t(
              'actionsPage.orientYourCareer.leadActionsAsPartOfYourCurrentJob'
            )}
          </Typography>
        </li>
      </ul>
    </Box>
  );
};

export default OrientYourCareer;
