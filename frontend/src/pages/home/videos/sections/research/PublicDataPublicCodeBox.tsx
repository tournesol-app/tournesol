import React from 'react';
import { Trans, useTranslation } from 'react-i18next';

import { Box, Link, Typography, Button, SxProps } from '@mui/material';
import { Download, GitHub } from '@mui/icons-material';

import { ExternalLink, TitledPaper } from 'src/components';
import TalksBox from './TalksBox';

const PublicDataPublicCodeBox = ({ sx }: { sx?: SxProps }) => {
  const apiUrl = import.meta.env.REACT_APP_API_URL;
  const { t } = useTranslation();

  return (
    <Box sx={sx}>
      <TitledPaper
        title={t('publicDataPublicCodeBox.ourDataAreOpen')}
        sx={{ mb: 2 }}
      >
        <>
          <Typography paragraph>
            {t('publicDataPublicCodeBox.weHopeThatOtherProjectsCanBenefitEtc')}
          </Typography>
          <Typography paragraph>
            <Trans i18nKey="publicDataPublicCodeBox.theseDataArePublishedUnderODCBY">
              These data are published under the terms of the Open Data Commons
              Attribution License
              <ExternalLink href="https://opendatacommons.org/licenses/by/summary/">
                (ODC-BY 1.0).
              </ExternalLink>
            </Trans>
          </Typography>
          <Box display="flex" justifyContent="center">
            <Button
              variant="contained"
              component={Link}
              href={`${apiUrl}/exports/all/`}
              startIcon={<Download />}
            >
              {t('publicDataPublicCodeBox.downloadTheDatabase')}
            </Button>
          </Box>
        </>
      </TitledPaper>
      <TitledPaper
        title={t('publicDataPublicCodeBox.ourAlgorithmsAreFree')}
        sx={{ mb: 2 }}
      >
        <>
          <Typography paragraph>
            {t(
              'publicDataPublicCodeBox.ourAlgorithmsAndAllOurCodeAreFreeSoftware'
            )}
          </Typography>
          <Box display="flex" justifyContent="center">
            <Button
              variant="contained"
              component={Link}
              href="https://github.com/tournesol-app/tournesol"
              startIcon={<GitHub />}
            >
              {t('publicDataPublicCodeBox.accessTheCodeOnGitHub')}
            </Button>
          </Box>
        </>
      </TitledPaper>
      <TalksBox />
    </Box>
  );
};

export default PublicDataPublicCodeBox;
