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

  const isLastItem = (idx: number) => {
    return idx === children.length - 1;
  };

  return (
    <Grid container width="100%">
      {children.map((child: React.ReactNode, i: number) =>
        isLastItem(i) ? (
          <SectionGridItem
            key={i}
            child={child}
            verticalPadding={verticalPadding}
            color={
              lastItemIsPrimary
                ? theme.palette.text.primary
                : i % 2 == 0
                ? secondaryColor
                : theme.palette.text.primary
            }
            background={
              lastItemIsPrimary
                ? theme.palette.background.primary
                : i % 2 == 0
                ? secondaryBackground
                : theme.palette.background.primary
            }
          />
        ) : (
          <SectionGridItem
            key={i}
            child={child}
            verticalPadding={
              i == 0 ? firstElemVerticalPadding : verticalPadding
            }
            color={i % 2 == 0 ? secondaryColor : theme.palette.text.primary}
            background={
              i % 2 == 0
                ? secondaryBackground
                : theme.palette.background.primary
            }
          />
        )
      )}
    </Grid>
  );
};

export default AlternatingBackgroundColorSectionList;
