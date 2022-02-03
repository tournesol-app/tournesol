import React, { useState } from 'react';
import { Box, Tabs, Tab } from '@mui/material';
import { useTranslation } from 'react-i18next';

interface Props extends React.HTMLAttributes<HTMLElement> {
  onMouseDown?: React.MouseEventHandler<HTMLElement>;
}

enum SelectorTabs {
  RateLater = 'rate-later',
  Recommendations = 'recommendations',
  RecentlyCompared = 'recently-compared',
}

const SelectorListbox = React.forwardRef(function SelectorListbox(
  props: Props,
  ref
) {
  const { t } = useTranslation();
  const [tabValue, setTabValue] = useState(SelectorTabs.RateLater);
  const { children, onMouseDown, ...rest } = props;

  const tabsLabels = {
    [SelectorTabs.RateLater]: t('Rate later'),
    [SelectorTabs.Recommendations]: t('Recommendations'),
    [SelectorTabs.RecentlyCompared]: t('Recently compared'),
  };

  console.info('REST', rest);

  return (
    <Box ref={ref} onMouseDown={onMouseDown}>
      <Tabs
        textColor="inherit"
        value={tabValue}
        onChange={(e, value) => setTabValue(value)}
        variant="scrollable"
        scrollButtons="auto"
        sx={{
          bgcolor: 'background.menu',
          '& .MuiTabs-scrollButtons.Mui-disabled': {
            opacity: 0.3,
          },
        }}
      >
        {Object.entries(tabsLabels).map(([value, label]) => (
          <Tab key={value} value={value} label={label} />
        ))}
      </Tabs>
      <ul {...rest}>{children}</ul>
    </Box>
  );
});

export default SelectorListbox;
