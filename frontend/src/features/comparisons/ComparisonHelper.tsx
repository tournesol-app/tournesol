import React, { useState } from 'react';

import ComparisonHelperPresidentielle2022 from './ComparisonHelperPresidentielle2022';
import { useCurrentPoll } from 'src/hooks/useCurrentPoll';
import { Button, Collapse } from '@mui/material';
import { ExpandMore, ExpandLess } from '@mui/icons-material';

const ComparisonHelper = () => {
  const [showHelp, setShowHelp] = useState(false);
  const { name: pollName } = useCurrentPoll();

  let content = null;

  if (pollName == 'presidentielle2022') {
    content = <ComparisonHelperPresidentielle2022 />;
  }

  return content ? (
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
        {showHelp ? 'Hide Help' : 'Show help for the comparison'}
      </Button>
    </>
  ) : null;
};

export default ComparisonHelper;
