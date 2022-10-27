import React from 'react';

import { Grid, useTheme } from '@mui/material';

const SectionGridItem = ({
  child,
  color,
  background,
  verticalPadding,
}: {
  child: React.ReactNode;
  color: string;
  background: string;
  verticalPadding: string;
}) => {
  const theme = useTheme();

  return (
    <Grid
      item
      xs={12}
      sx={{
        display: 'flex',
        justifyContent: 'center',
        padding: verticalPadding,
        [theme.breakpoints.down('md')]: {
          padding: `${verticalPadding} 16px ${verticalPadding} 16px`,
        },
        color: color,
        background: background,
      }}
    >
      {child}
    </Grid>
  );
};

const AlternatingBackgroundColorSectionList = ({
  children,
  secondaryBackground = '#1282B2',
  secondaryColor = 'white',
  verticalPadding = '48px',
  firstElemVerticalPadding = '32px',
  lastItemIsPrimary,
}: {
  children: React.ReactNode[];
  secondaryBackground?: string;
  secondaryColor?: string;
  // Allow the first item to have a different padding than the rest of the
  // items.
  firstElemVerticalPadding?: string;
  // Used to wrap every item.
  verticalPadding?: string;
  // If true the last item will use the primary color regardless of its
  // position in the list.
  lastItemIsPrimary?: boolean;
}) => {
  const theme = useTheme();

  // children.at(-1) didn't work here...
  const lastItem = children.slice(children.length - 1);

  const nextColor = (idx: number): string => {
    return idx % 2 == 0 ? secondaryColor : theme.palette.text.primary;
  };

  const nextBackground = (idx: number): string => {
    return idx % 2 == 0
      ? secondaryBackground
      : theme.palette.background.primary;
  };

  return (
    <Grid container width="100%">
      {/* display all items except the last one */}
      {children.slice(0, -1).map((child: React.ReactNode, i: number) => (
        <SectionGridItem
          key={i}
          child={child}
          verticalPadding={i == 0 ? firstElemVerticalPadding : verticalPadding}
          color={nextColor(i)}
          background={nextBackground(i)}
        />
      ))}

      {/* display the last item */}
      <SectionGridItem
        child={lastItem}
        verticalPadding={verticalPadding}
        color={
          lastItemIsPrimary
            ? theme.palette.text.primary
            : children.length % 2 != 0
            ? secondaryColor
            : theme.palette.text.primary
        }
        background={
          lastItemIsPrimary
            ? theme.palette.background.primary
            : children.length % 2 != 0
            ? secondaryBackground
            : theme.palette.background.primary
        }
      />
    </Grid>
  );
};

export default AlternatingBackgroundColorSectionList;
