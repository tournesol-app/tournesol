import React from 'react';
import { Trans, useTranslation } from 'react-i18next';
import { Link } from 'react-router-dom';

import { Box, Button, Grid2, Paper, Typography, useTheme } from '@mui/material';
import { VolunteerActivism } from '@mui/icons-material';

import SectionTitle from './SectionTitle';
import SectionDescription from './SectionDescription';

interface FundingSectionProps {
  linkToDonatePage?: boolean;
}

const FundingSection = ({ linkToDonatePage = true }: FundingSectionProps) => {
  const theme = useTheme();
  const { t } = useTranslation();

  const motivationSx = {
    m: 0,
    textAlign: 'center',
    '& span': {
      color: theme.palette.primary.main,
      textTransform: 'uppercase',
    },
  };

  return (
    <>
      <SectionTitle title={t('fundingSection.supportUs')} headingId="funding" />
      <SectionDescription
        description={t('fundingSection.tournesolExistsThanksToYourInvolvement')}
      />
      <Grid2
        container
        spacing={4}
        sx={{
          justifyContent: 'center',
        }}
      >
        <Grid2
          size={{
            sm: 12,
            md: 4,
            lg: 4,
          }}
        >
          <Paper elevation={0}>
            <Box
              sx={{
                p: 2,
                height: '110px',
                display: 'flex',
                justifyContent: 'center',
                alignItems: 'center',
                color: '#fff',
                bgcolor: '#1282B2',
                borderRadius: 1,
              }}
            >
              <Typography variant="h4" sx={motivationSx}>
                <Trans i18nKey="fundingSection.guaranteeTheProjectsIndependence">
                  <span>guarantee</span> the project&apos;s independance
                </Trans>
              </Typography>
            </Box>
          </Paper>
        </Grid2>
        <Grid2
          size={{
            sm: 12,
            md: 4,
            lg: 4,
          }}
        >
          <Paper elevation={0}>
            <Box
              sx={{
                p: 2,
                height: '110px',
                display: 'flex',
                justifyContent: 'center',
                alignItems: 'center',
                color: '#fff',
                bgcolor: '#1282B2',
                borderRadius: 1,
              }}
            >
              <Typography variant="h4" sx={motivationSx}>
                <Trans i18nKey="fundingSection.participateInTheCreationOfCommons">
                  <span>participate</span> in the creation of commons
                </Trans>
              </Typography>
            </Box>
          </Paper>
        </Grid2>
        <Grid2
          size={{
            sm: 12,
            md: 4,
            lg: 4,
          }}
        >
          <Paper elevation={0}>
            <Box
              sx={{
                p: 2,
                height: '110px',
                display: 'flex',
                justifyContent: 'center',
                alignItems: 'center',
                color: '#fff',
                bgcolor: '#1282B2',
                borderRadius: 1,
              }}
            >
              <Typography variant="h4" sx={motivationSx}>
                <Trans i18nKey="fundingSection.actForTheEthicsOfInformation">
                  <span>act</span> for the ethics of information
                </Trans>
              </Typography>
            </Box>
          </Paper>
        </Grid2>
        {linkToDonatePage && (
          <Grid2
            size={12}
            sx={{
              display: 'flex',
              justifyContent: 'center',
            }}
          >
            <Button
              fullWidth
              variant="contained"
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
