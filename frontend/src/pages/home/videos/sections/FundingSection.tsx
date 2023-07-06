import React from 'react';
import { Trans, useTranslation } from 'react-i18next';
import { Link } from 'react-router-dom';

import { Box, Button, Paper, Typography, useTheme } from '@mui/material';
import Grid2 from '@mui/material/Unstable_Grid2/Grid2';
import { VolunteerActivism } from '@mui/icons-material';

import SectionTitle from './SectionTitle';

interface FundingSectionProps {
  linkToDonatePage?: boolean;
  fullWidth?: boolean;
}

const FundingSection = ({
  linkToDonatePage = true,
  fullWidth = false,
}: FundingSectionProps) => {
  const theme = useTheme();
  const { t } = useTranslation();

  const motivationSx = {
    '& span': {
      color: theme.palette.primary.main,
      textTransform: 'uppercase',
    },
  };

  return (
    <>
      <SectionTitle
        title={t('fundingSection.supportUs')}
        dividerWidthXl={fullWidth ? '100%' : undefined}
        headingId="funding"
      />
      <Box display="flex" justifyContent="center" mb={6}>
        <Box sx={{ width: { lg: '44%', xl: '44%' } }}>
          <Typography variant="h3" textAlign="center" letterSpacing="0.8px">
            {t('fundingSection.tournesolExistsThanksToYourInvolvement')}
          </Typography>
        </Box>
      </Box>
      <Grid2 container spacing={4} justifyContent="center">
        <Grid2 sm={12} md={4} lg={4} xl={fullWidth ? 4 : 3}>
          <Paper elevation={0}>
            <Box
              p={2}
              height="110px"
              display="flex"
              justifyContent="center"
              alignItems="center"
              color="#fff"
              bgcolor="#1282B2"
              borderRadius={1}
            >
              <Typography
                m={0}
                variant="h4"
                textAlign="center"
                sx={motivationSx}
              >
                <Trans i18nKey="fundingSection.guaranteeTheProjectsIndependence">
                  <span>guarantee</span> the project&apos;s independance
                </Trans>
              </Typography>
            </Box>
          </Paper>
        </Grid2>
        <Grid2 sm={12} md={4} lg={4} xl={fullWidth ? 4 : 3}>
          <Paper elevation={0}>
            <Box
              p={2}
              height="110px"
              display="flex"
              justifyContent="center"
              alignItems="center"
              color="#fff"
              bgcolor="#1282B2"
              borderRadius={1}
            >
              <Typography
                m={0}
                variant="h4"
                textAlign="center"
                sx={motivationSx}
              >
                <Trans i18nKey="fundingSection.participateInTheCreationOfCommons">
                  <span>participate</span> in the creation of commons
                </Trans>
              </Typography>
            </Box>
          </Paper>
        </Grid2>
        <Grid2 sm={12} md={4} lg={4} xl={fullWidth ? 4 : 3}>
          <Paper elevation={0}>
            <Box
              p={2}
              height="110px"
              display="flex"
              justifyContent="center"
              alignItems="center"
              color="#fff"
              bgcolor="#1282B2"
              borderRadius={1}
            >
              <Typography
                m={0}
                variant="h4"
                textAlign="center"
                sx={motivationSx}
              >
                <Trans i18nKey="fundingSection.actForTheEthicsOfInformation">
                  <span>act</span> for the ethics of information
                </Trans>
              </Typography>
            </Box>
          </Paper>
        </Grid2>
        {linkToDonatePage && (
          <Grid2 xs={9} display="flex" justifyContent="center">
            <Button
              variant="contained"
              size="large"
              component={Link}
              to="/about/donate"
              startIcon={<VolunteerActivism />}
            >
              {t('fundingSection.iSupport')}
            </Button>
          </Grid2>
        )}
      </Grid2>
    </>
  );
};

export default FundingSection;
