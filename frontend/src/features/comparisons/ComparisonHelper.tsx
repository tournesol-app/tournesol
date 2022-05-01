import React, { useState } from 'react';
import { Button, Collapse } from '@mui/material';
import { ExpandMore, ExpandLess } from '@mui/icons-material';
import { useTranslation } from 'react-i18next';

import { PRESIDENTIELLE_2022_POLL_NAME } from 'src/utils/constants';
import { useCurrentPoll } from 'src/hooks/useCurrentPoll';

import ComparisonHelperPresidentielle2022 from './ComparisonHelperPresidentielle2022';

const ComparisonHelper = () => {
  const [showHelp, setShowHelp] = useState(false);
  const { name: pollName } = useCurrentPoll();
  const { t } = useTranslation();

  let content = null;

  if (pollName == PRESIDENTIELLE_2022_POLL_NAME) {
    content = <ComparisonHelperPresidentielle2022 />;
  }

  if (!content) return null;

  return (
    <>
      <Collapse in={showHelp} timeout="auto" sx={{ width: '100%' }}>
        {content}
      </Collapse>
      <Button
        onClick={() => setShowHelp(!showHelp)}
        startIcon={!showHelp ? <ExpandMore /> : <ExpandLess />}
        size="small"
        color="secondary"
      >
        {showHelp
          ? t('comparisonHelper.hideHelp')
          : t('comparisonHelper.showHelp')}
      </Button>
    </>
  );
};

export default ComparisonHelper;
