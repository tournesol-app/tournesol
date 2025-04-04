import React from 'react';

import { useTranslation } from 'react-i18next';

import { Box } from '@mui/material';

import { ContentBox, ContentHeader } from 'src/components';

const ProofByKeywordPage = () => {
  const { t } = useTranslation();

  return (
    <>
      <ContentHeader title="Mes statistiques" />
      <ContentBox maxWidth="xl">
        <Box></Box>
      </ContentBox>
    </>
  );
};

export default ProofByKeywordPage;
