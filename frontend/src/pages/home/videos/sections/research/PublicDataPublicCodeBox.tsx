import React from 'react';
import { Link as RouterLink } from 'react-router-dom';
import { Trans, useTranslation } from 'react-i18next';

import { Box, Link, Paper, Typography, Button, SxProps } from '@mui/material';
import { Download, GitHub } from '@mui/icons-material';

const PublicDataPublicCodeBox = ({ sx }: { sx?: SxProps }) => {
  const apiUrl = process.env.REACT_APP_API_URL;
  const { t } = useTranslation();

  return (
    <Box sx={sx}>
      <Paper sx={{ mb: 2 }}>
        <Box
          p={2}
          color="#fff"
          bgcolor="#1282B2"
          sx={{
            borderTopLeftRadius: 'inherit',
            borderTopRightRadius: 'inherit',
          }}
        >
          <Typography variant="h4">
            {t('publicDataPublicCodeBox.ourDataAreOpen')}
          </Typography>
        </Box>
        <Box p={2}>
          <Typography paragraph>
            {t('publicDataPublicCodeBox.tournesolIsAnOpenlyAltruisticProject')}
          </Typography>
          <Typography paragraph>
            {t('publicDataPublicCodeBox.weHopeThatOtherProjectsCanBenefitEtc')}
          </Typography>
          <Typography paragraph>
            <Trans i18nKey="publicDataPublicCodeBox.theseDataArePublishedUnderODCBY">
              These data are published under the terms of the Open Data Commons
              Attribution License
              <Link
                color="text.primary"
                href="https://opendatacommons.org/licenses/by/summary/"
              >
                (ODC-BY 1.0).
              </Link>
            </Trans>
          </Typography>
        </Box>
      </Paper>
      <Paper sx={{ p: 2, mb: 2 }}>
        <Box display="flex" justifyContent="center">
          <Button
            variant="contained"
            component={RouterLink}
            to={`${apiUrl}/exports/all/`}
            endIcon={<Download />}
          >
            {t('publicDataPublicCodeBox.downloadTheDatabase')}
          </Button>
        </Box>
      </Paper>
      <Paper sx={{ p: 2 }}>
        <Box display="flex" justifyContent="center">
          <Button
            variant="contained"
            component={Link}
            target="_blank"
            rel="noopener"
            href="https://github.com/tournesol-app/tournesol"
            endIcon={<GitHub />}
          >
            {t('publicDataPublicCodeBox.accessTheCodeOnGitHub')}
          </Button>
        </Box>
      </Paper>
    </Box>
  );
};

export default PublicDataPublicCodeBox;
