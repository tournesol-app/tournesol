import React from 'react';
import { Link } from 'react-router-dom';
import { useTranslation } from 'react-i18next';

import { Box, Typography, Button } from '@mui/material';
import { Lightbulb } from '@mui/icons-material';

import TitledPaper from 'src/components/TitledPaper';

const TalksBox = () => {
  const { t } = useTranslation();

  return (
    <TitledPaper
      title={t('publicDataPublicCodeBox.discoverTheTalks')}
      sx={{ mb: 2 }}
    >
      <>
        <Typography
          sx={{
            marginBottom: 2,
          }}
        >
          {t('publicDataPublicCodeBox.weOrganizePublicEvents')}
        </Typography>
        <Box
          sx={{
            display: 'flex',
            justifyContent: 'center',
          }}
        >
          <Button
            variant="contained"
            color="primary"
            component={Link}
            to={'/talks'}
            startIcon={<Lightbulb />}
          >
            {t('publicDataPublicCodeBox.accessTalksPage')}
          </Button>
        </Box>
      </>
    </TitledPaper>
  );
};

export default TalksBox;
