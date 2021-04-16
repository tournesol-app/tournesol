// variables starting with underscore can be unused
/* eslint no-unused-vars: ["error", { "argsIgnorePattern": "^_" }] */

import React from 'react';

import { makeStyles } from '@material-ui/core/styles';
import FormControl from '@material-ui/core/FormControl';
import NativeSelect from '@material-ui/core/NativeSelect';
import TextField from '@material-ui/core/TextField';
import InputLabel from '@material-ui/core/InputLabel';
import Autocomplete from '@material-ui/lab/Autocomplete';
import { TournesolAPI } from '../../api';

const useStyles = makeStyles(() => ({
  main: {
    display: 'flex',
    flexDirection: 'column',
    width: '100%',
  },
  select: {
    marginTop: '8px',
  },
}));

export default ({ options, setOptions }) => {
  const classes = useStyles();
  const [requested, setRequested] = React.useState(false);
  const [modelsList, setModelsList] = React.useState([]);

  if (!requested) {
    setRequested(true);
    const api = new TournesolAPI.UserInformationApi();
    api.userInformationPublicModelsList({ limit: 1000 }, (err, data) => {
      if (!err) {
        setModelsList(data.results.map((x) => x.username));
      }
    });
  }

  const update = (field) => (x) => {
    setOptions({ ...options, [field]: x.target.value });
  };

  return (
    <div className={`${classes.main} all_search_options`}>
      <FormControl className={classes.select}>
        <InputLabel htmlFor="age-native-helper">Minimum Duration</InputLabel>
        <NativeSelect
          value={options.durationGte}
          onChange={update('durationGte')}
        >
          <option value={0}>0 min</option>
          <option value={2 * 60}>2 min</option>
          <option value={5 * 60}>5 min</option>
          <option value={15 * 60}>15 min</option>
          <option value={30 * 60}>30 min</option>
          <option value={60 * 60}>1 hour</option>
        </NativeSelect>
      </FormControl>
      <FormControl className={classes.select}>
        <InputLabel htmlFor="age-native-helper">Maximum Duration</InputLabel>
        <NativeSelect
          value={options.durationLte}
          onChange={update('durationLte')}
        >
          <option value={2 * 60}>2 min</option>
          <option value={5 * 60}>5 min</option>
          <option value={15 * 60}>15 min</option>
          <option value={30 * 60}>30 min</option>
          <option value={60 * 60}>1 hour</option>
          <option value="--null">Unlimited</option>
        </NativeSelect>
      </FormControl>
      <FormControl className={classes.select}>
        <InputLabel htmlFor="age-native-helper">
          Minimum Number of Views
        </InputLabel>
        <NativeSelect value={options.viewsGte} onChange={update('viewsGte')}>
          <option value={0}>0 views</option>
          <option value={10000}>10k views</option>
          <option value={1000000}>1M views</option>
        </NativeSelect>
      </FormControl>
      <FormControl className={classes.select}>
        <InputLabel htmlFor="age-native-helper">
          Maximum Number of Views
        </InputLabel>
        <NativeSelect value={options.viewsLte} onChange={update('viewsLte')}>
          <option value={10000}>10k views</option>
          <option value={1000000}>1M views</option>
          <option value="--null">Unlimited</option>
        </NativeSelect>
      </FormControl>
      <FormControl className={classes.select}>
        <InputLabel htmlFor="age-native-helper">Publication Date</InputLabel>
        <NativeSelect value={options.daysAgoLte} onChange={update('daysAgoLte')}>
          <option value="--null">No limit</option>
          <option value="365">Last year</option>
          <option value="30">Last month</option>
        </NativeSelect>
      </FormControl>
      <FormControl className={classes.select}>
        <InputLabel htmlFor="age-native-helper">Language</InputLabel>
        <NativeSelect value={options.language} onChange={update('language')}>
          <option value="--null">Any</option>
          <option value="en">English</option>
          <option value="fr">Français</option>
          <option value="de">Deutsch</option>
        </NativeSelect>
      </FormControl>
      <FormControl className={classes.select}>
        <InputLabel htmlFor="age-native-helper">Search engine</InputLabel>
        <NativeSelect value={options.searchYTRaw} onChange={update('searchYTRaw')}>
          <option value="false">Tournesol</option>
          <option value="true">Youtube</option>
        </NativeSelect>
      </FormControl>
      <FormControl className={classes.select}>
        <Autocomplete
          id="autocomplete_search_model"
          options={['--null'].concat(modelsList)}
          getOptionLabel={(option) => (option === '--null' ?
            'Aggregated' : `${option}'s representative`)}
          disableClearable
          value={options.searchModel}
          onChange={(_event, value) => {
            setOptions({ ...options, searchModel: value });
          }}
          renderInput={(params) => <TextField
            {...params} // eslint-disable-line react/jsx-props-no-spreading
            label="Search model"
            margin="normal"
          />}
        />
      </FormControl>
      {options.searchModel === window.username && (
      <FormControl className={classes.select}>
        <InputLabel htmlFor="age-native-helper">Show all videos</InputLabel>
        <NativeSelect value={options.showAllMyVideos} onChange={update('showAllMyVideos')}>
          <option value="false">No</option>
          <option value="true">Yes</option>
        </NativeSelect>
      </FormControl>
      )}
    </div>
  );
};
