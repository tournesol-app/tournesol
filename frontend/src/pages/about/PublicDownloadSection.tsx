import React, { useContext, useEffect, useState } from 'react';
import { useTranslation, Trans } from 'react-i18next';

import { Typography, Button } from '@mui/material';

import { getPollStats } from 'src/features/statistics/stats';
import { useCurrentPoll } from 'src/hooks';
import { StatsContext } from 'src/features/comparisons/StatsContext';
import { Statistics } from 'src/services/openapi';

// PublicDownloadSection is a paragraph displayed on the HomePage
// that helps users know how to download the public video comparisons available for their use case
const PublicDownloadSection = () => {
  const { t } = useTranslation();
  const { name: pollName } = useCurrentPoll();

  const [stats, setStats] = useState<Statistics>();

  const api_url = process.env.REACT_APP_API_URL;

  const { getStats } = useContext(StatsContext);
  useEffect(() => {
    setStats(getStats());
  }, [getStats]);

  const pollStats = getPollStats(stats, pollName);

  const userCount = stats?.active_users.total ?? 0;
  const comparisonCount = pollStats?.comparisons.total ?? 0;
  const comparedEntityCount = pollStats?.compared_entities.total ?? 0;

  return (
    <>
      <Typography variant="h1">{t('about.publicDatabase')}</Typography>
      <Typography paragraph>
        <Trans t={t} i18nKey="about.publicDatabaseDetailAndLicense">
          Contributors on Tournesol can decide to make their data public. We
          hope this important data will prove useful for researchers on ethics
          of algorithms and large scale recommender systems. Our public database
          can be downloaded by clicking the button below and is published under{' '}
          <a
            href="https://opendatacommons.org/licenses/by/1-0/"
            style={{ color: 'white' }}
          >
            Open Data Commons Attribution License (ODC-By)
          </a>
          .
        </Trans>
      </Typography>
      <Typography paragraph>
        <Trans t={t} i18nKey="about.publicDatabaseThanksToContributors">
          Finally, we would like to thank all the contributors who compared
          videos on Tournesol. We count so far about {{ userCount }} users who
          compared {{ comparisonCount }} times more than{' '}
          {{ comparedEntityCount }} videos.
        </Trans>
      </Typography>

      <Button
        component="a"
        href={`${api_url}/exports/all/`}
        download="tournesol_public_export.csv"
        color="primary"
        variant="contained"
      >
        {t('clickToDownload')}
      </Button>
    </>
  );
};

export default PublicDownloadSection;
