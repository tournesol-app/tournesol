import React from 'react';
import { Trans, useTranslation } from 'react-i18next';
import { Link } from 'react-router-dom';

import { Box, Button, Grid2, Paper, Typography, useTheme } from '@mui/material';
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
    m: 0,
    textAlign: 'center',
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
      <Box
        sx={{
          display: 'flex',
          justifyContent: 'center',
          mb: 6,
        }}
      >
        <Box sx={{ width: { lg: '44%', xl: '44%' } }}>
          <Typography
            variant="h3"
            sx={{
              textAlign: 'center',
              letterSpacing: '0.8px',
            }}
          >
            {t('fundingSection.tournesolExistsThanksToYourInvolvement')}
          </Typography>
        </Box>
      </Box>
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
            xl: fullWidth ? 4 : 3,
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
            xl: fullWidth ? 4 : 3,
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
            xl: fullWidth ? 4 : 3,
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
            size={9}
            sx={{
              display: 'flex',
              justifyContent: 'center',
            }}
          >
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
