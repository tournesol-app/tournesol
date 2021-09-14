import React from 'react';

import {
  FormControlLabel,
  makeStyles,
  Typography,
  Checkbox,
  Collapse,
  Button,
} from '@material-ui/core';
import {
  CheckCircle,
  CheckCircleOutline,
  ExpandLess,
  ExpandMore,
} from '@material-ui/icons';

const useStyles = makeStyles(() => ({
  main: {
    margin: 4,
  },
  filter: {
    color: '#506AD4',
    margin: '8px',
  },
  collapse: {
    display: 'flex',
    flexWrap: 'wrap',
    alignContent: 'space-between',
  },
}));

function SearchFilter(props: {
  date: string;
  language: string;
  onChange: (e: React.ChangeEvent<HTMLInputElement>) => void;
}) {
  const classes = useStyles();
  const [expanded, setExpanded] = React.useState(false);
  const dateChoices = ['Any', 'Today', 'Week', 'Month', 'Year'];
  const languageChoices = ['English', 'French'];

  const handleExpandClick = () => {
    setExpanded(!expanded);
  };

  return (
    <div className="main">
      <Button
        color="secondary"
        size="large"
        className={classes.filter}
        startIcon={!expanded ? <ExpandMore /> : <ExpandLess />}
        aria-expanded={expanded}
        aria-label="show more"
        onClick={handleExpandClick}
      >
        Filters
      </Button>
      <Collapse
        className={classes.collapse}
        in={expanded}
        timeout="auto"
        unmountOnExit
      >
        <div className="data uploaded">
          <Typography variant="h5" component="h2">
            Date Uploaded
          </Typography>
          {dateChoices.map((label) => (
            <FormControlLabel
              control={
                <Checkbox
                  icon={<CheckCircleOutline />}
                  checkedIcon={<CheckCircle />}
                  checked={props.date == label}
                  onChange={props.onChange}
                  name={label}
                />
              }
              label={label}
              key={label}
            />
          ))}
        </div>
        <div className="language">
          <Typography variant="h5" component="h2">
            Language
          </Typography>
          {languageChoices.map((label) => (
            <FormControlLabel
              control={
                <Checkbox
                  icon={<CheckCircleOutline />}
                  checkedIcon={<CheckCircle />}
                  checked={props.language == label}
                  onChange={props.onChange}
                  name={label}
                />
              }
              label={label}
              key={label}
            />
          ))}
        </div>
      </Collapse>
    </div>
  );
}

export default SearchFilter;
