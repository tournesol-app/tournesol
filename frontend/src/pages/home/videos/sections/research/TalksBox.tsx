import React from 'react';
import { Link } from 'react-router-dom';
import { useTranslation } from 'react-i18next';

import { Box, Typography, Button, SxProps } from '@mui/material';

import TitledPaper from 'src/components/TitledPaper';
import { Lightbulb } from '@mui/icons-material';

const TalksBox = ({ sx }: { sx?: SxProps }) => {
  const { t } = useTranslation();

  return (
    <Box sx={sx}>
      <TitledPaper
        title={t('publicDataPublicCodeBox.discoverTheTalks')}
        sx={{ mb: 2 }}
      >
        <>
          <Typography paragraph>
            {t('talksPage.tournesolTalksIntroduction')}
          </Typography>
          <Box display="flex" justifyContent="center">
            <Button
              variant="contained"
              color="primary"
              component={Link}
              to={'/talks'}
              endIcon={<Lightbulb />}
            >
              {t('publicDataPublicCodeBox.accessTalksPage')}
            </Button>
          </Box>
        </>
      </TitledPaper>
    </Box>
  );
};

export default TalksBox;
