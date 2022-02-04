import React, { useContext, useState } from 'react';
import { Box, Tabs, Tab, Drawer, Paper } from '@mui/material';
import { useTranslation } from 'react-i18next';
import { useLoginState } from 'src/hooks';
import { AutocompleteContext } from './VideoSelector';

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
  ref: React.ForwardedRef<HTMLDivElement>
) {
  const { t } = useTranslation();
  const { isLoggedIn } = useLoginState();
  const [tabValue, setTabValue] = useState(SelectorTabs.RateLater);
  const { children, onMouseDown, ...rest } = props;

  //   const { open, setOpen } = useContext(AutocompleteContext);

  const tabsItems = [
    {
      value: SelectorTabs.RateLater,
      label: t('Rate later'),
      disabled: !isLoggedIn,
    },
    {
      value: SelectorTabs.RecentlyCompared,
      label: t('Recently compared'),
      disabled: !isLoggedIn,
    },
    {
      value: SelectorTabs.Recommendations,
      label: t('Recommendations'),
    },
  ];

  return (
    // <Drawer
    //   anchor="bottom"
    //   ref={ref}
    //   open={open}
    //   onClose={() => setOpen(false)}
    //   ModalProps={{
    //     disableEnforceFocus: true,
    //     disableRestoreFocus: true,
    //     BackdropProps: {
    //       invisible: true,
    //     },
    //   }}
    //   variant="persistent"
    //   //   sx={{ pointerEvents: 'none' }}
    // >
    <Paper
      elevation={10}
      onMouseDown={onMouseDown}
      sx={{
        '& .MuiAutocomplete-option': {
          p: 0,
        },
        '& .MuiAutocomplete-option[aria-selected="true"]': {
          bgcolor: 'action.selected',
          '&.Mui-focused': {
            bgcolor: 'action.selected',
          },
        },
        ul: {
          listStyleType: 'none',
          p: 0,
          overflowY: 'scroll',
          maxHeight: '40vh',
          marginTop: 1,
          marginBottom: 0,
        },
        li: {
          cursor: 'pointer',
          '&:hover': {
            bgcolor: 'action.selected',
          },
        },
        width: 'min(700px, 100vw)',
        bgcolor: 'white',
        overflow: 'hidden',
      }}
    >
      <Tabs
        textColor="inherit"
        value={tabValue}
        onChange={(e, value) => setTabValue(value)}
        variant="scrollable"
        scrollButtons="auto"
        sx={{
          bgcolor: 'background.menu',
          borderBottom: '1px solid rgba(0, 0, 0, 0.12)',
          '& .MuiTabs-scrollButtons.Mui-disabled': {
            opacity: 0.3,
          },
        }}
      >
        {tabsItems.map(({ label, value, disabled }) => (
          <Tab key={value} value={value} label={label} disabled={disabled} />
        ))}
      </Tabs>
      <ul {...rest}>{children}</ul>
    </Paper>
    // </Drawer>
  );
});

export default SelectorListbox;
