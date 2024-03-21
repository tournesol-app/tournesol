import React from 'react';
import { Trans, useTranslation } from 'react-i18next';

import { Box, Link, Typography } from '@mui/material';

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
              <Link
                href="https://waitbutwhy.com/2018/04/picking-career.html"
                target="_blank"
                rel="noopener"
                sx={{
                  color: 'revert',
                  textDecoration: 'revert',
                }}
              >
                How to pick a career (that actually fits you)
              </Link>
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
