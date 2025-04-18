import React from 'react';
import { Button, Menu, Theme } from '@mui/material';
import { ArrowDropDown } from '@mui/icons-material';

interface Props {
  className?: string;
  startIcon?: React.ReactNode;
  menuContent?: React.ReactNode;
  children?: React.ReactNode;
  menuProps?: Record<string, unknown>;
  [rest: string]: unknown;
}

const MenuButton = ({
  className,
  startIcon,
  menuContent,
  children,
  menuProps,
  ...rest
}: Props) => {
  const [anchorEl, setAnchorEl] = React.useState<null | HTMLElement>(null);
  const closeMenu = () => setAnchorEl(null);

  return (
    <>
      <Button
        variant="text"
        color="inherit"
        className={className}
        startIcon={startIcon}
        endIcon={<ArrowDropDown />}
        onClick={(e) => setAnchorEl(e.currentTarget)}
        size="large"
        {...rest}
      >
        {children}
      </Button>
      <Menu
        open={Boolean(anchorEl)}
        anchorEl={anchorEl}
        onClose={closeMenu}
        {...menuProps}
        slotProps={{
          list: {
            onClick: () => closeMenu(),
            sx: {
              backgroundColor: (t: Theme) => t.palette.background.menu,
              '& .MuiListItemIcon-root': { color: '#CDCABC' },
            },
          },
        }}
      >
        {menuContent}
      </Menu>
    </>
  );
};

export default MenuButton;
