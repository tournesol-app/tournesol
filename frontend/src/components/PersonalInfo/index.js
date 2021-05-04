import React, { useState } from 'react';

import { makeStyles } from '@material-ui/core/styles';
import Alert from '@material-ui/lab/Alert';
import Form, { Widgets } from '@rjsf/material-ui';
import Autocomplete from '@material-ui/lab/Autocomplete';
import TextField from '@material-ui/core/TextField';
import Button from '@material-ui/core/Button';
import Grid from '@material-ui/core/Grid';
import { deleteFrom } from '../../utils';
import {
  errorToJsonError,
  formatError,
  fromOpenAPIToJsonSchema,
  recursiveIterDict,
  getSchema,
  TournesolAPI,
  undefinedToNullValue,
  urlToDataURL,
} from '../../api';
import DangerConfirm from './DangerConfirm';

/* eslint no-unused-vars: ["error", { "argsIgnorePattern": "^_" }] */

// do not show these fields
const ignoreFields = ['id', 'n_ratings', 'n_videos', 'n_likes', 'n_comments',
  'n_thanks_given', 'n_thanks_received', 'n_mentions', 'n_public_videos',
  'certified_email_domain'];

// do not show these titles
const blacklistTitles = ['E-mail', 'E-mail address', 'Degree', 'Expertise',
  'Expertise description', 'Expertise keyword',
  'Expertise keyword description'];

const useStyles = makeStyles(() => ({
  root: {
    display: 'flex',
    width: '900px',
    maxWidth: '100%',
    height: '100%',
    overflowY: 'auto',
    overflowX: 'hidden',
    flexDirection: 'column',
    padding: '8px',
  },
}));

// Help for different sections of the form
const helpText = {
  title_userprofile: (
    <>
      <h3>General information</h3>
      <i style={{ fontSize: '90%' }}>You can save the form by submitting it at any time.
        All information is optional. If
        you
        choose to write a
        comment under your own name, then your name will only appear in the comments. We may
        also use your data to
        provide global statistics of experts' preferences. Find out more by reading our
        privacy
        policy.
      </i>

    </>),
  title_email: (
    <>
      <Grid
        container
        spacing={2}
        direction="row"
        justify="center"
        alignItems="center"
      >
        <Grid item>
          <Button
            href="/change_username"
            id="id_change_username"
            variant="contained"
            color="primary"
          >
            Change my login name
          </Button>
        </Grid>
        <Grid item>
          <Button
            href="/set_password"
            id="id_set_password"
            variant="contained"
            color="primary"
          >
            Change my password
          </Button>
        </Grid>
      </Grid>
      <h3>Your e-mail addresses</h3>
      <i style={{ fontSize: '90%' }}>Your email addresses will never be published. However
        confirmed emails from trusted
        institutions are critical
        to Tournesol, as they are what allow us to identify and authenticate experts.
        Registering and confirming an
        email from. a trusted institution will allow you to comment videos and will make
        your
        ratings count for
        Tournesol's scores.
        If you added a new email. A confirmation email will be sent to your mailbox once you
        have submitted the
        form
      </i>
      <a className="to_verified_domains_class" href="/email_domains">
        List of accepted domains
      </a>
    </>),
  title_degree: (
    <>
      <h3>Your education</h3>
      <i style={{ fontSize: '90%' }}>The list of your degrees will be shown on your user
        profile page and when
        you comment videos. We may also use them to provide global statistics on experts'
        preferences and to compute
        Tournesol's scores.
      </i>
    </>),
  title_expertise: (
    <>
      <h3>Your expertise</h3>
      <i style={{ fontSize: '90%' }}>The list of your expertise areas will be shown on your
        user profile page and
        when you comment videos. We may also use them to provide global statistics on
        experts'
        preferences and to
        compute Tournesol's scores.
      </i>
    </>),
  title_expertise_keywords: ' ',
  title_demographic: (
    <>
      <h3>Demographic data</h3>
      <i style={{ fontSize: '90%' }}>Such data mostly serve for the statistical
        analysis of the expert
        that contributed to Tournesol, and of differences of judgements between
        sub-populations.
        These data remain
        private. Only noisy global statistical data will be shared.
      </i>
    </>),
  title_online: (
    <>
      <Grid
        container
        spacing={2}
        direction="row"
        justify="center"
        alignItems="center"
      >
        <Grid item>
          <DangerConfirm
            buttonText="Make my videos private"
            explanation={'This will set all the videos you have rated as private.' +
                           ' Other people will not be able to see them. Are you sure?'}
            callback={(f) => {
              const api = new TournesolAPI.VideosApi();
              api.setAllRatingPrivacy(false, (err, _data) => {
                if (err) {
                  f('Operation failed', null);
                } else {
                  f(null, 'All ratings set as private! If you have many ratings' +
                  ', it might take up to one hour to update the list of contributors.');
                }
              });
              return null;
            }}
          />
        </Grid>

        <Grid item>
          <DangerConfirm
            buttonText="Make my videos public"
            explanation={'This will set all the videos you have rated as public.' +
               ' Other people will be able to see them. Are you sure?'}
            callback={(f) => {
              const api = new TournesolAPI.VideosApi();
              api.setAllRatingPrivacy(true, (err, _data) => {
                if (err) {
                  f('Operation failed', null);
                } else {
                  f(null, 'All ratings set as public! If you have many ratings' +
                  ', it might take up to one hour to update the list of contributors.');
                }
              });
              return null;
            }}
          />
        </Grid>
      </Grid>

      <h3>Your online presence</h3>
      <i style={{ fontSize: '90%' }}>Your can provide useful information to determine
        how much Tournesol
        should trust you. You can decide whether to publish these data on your Tournesol
        profile or
        not
      </i>
    </>),
};

// either help text or the text field
function CustomTextAreaWidget(props) {
  /* eslint-disable react/jsx-props-no-spreading */
  const { value = '' } = props;
  return <Widgets.TextareaWidget {...props} value={value} />;
  /* eslint-enable react/jsx-props-no-spreading */
}

// either help text or the text field
function HelpOrTextWidget(props) {
  // simple override by key

  const { label, value = '', id } = props;
  const [options, setOptions] = React.useState([]);
  const [requested, setRequested] = React.useState(false);
  const [running, setRunning] = React.useState(false);

  function updateOptions(search) {
    if (running) {
      return;
    }
    setRunning(true);
    const api = new TournesolAPI.UserInformationApi();
    api.userInformationSearchExpertiseList(search, {}, (err, data) => {
      if (!err) {
        setOptions(data.results.map((x) => x.name));
      }
      setRunning(false);
    });
  }

  if (!requested) {
    setRequested(true);
    updateOptions('');
  }

  if (id.includes('expertise') && !id.includes('title')) {
    return <Autocomplete
      freeSolo
      id={id}
      value={value}
      options={options}
      getOptionLabel={(option) => option}
      style={{ width: 300 }}
      onInputChange={(e, newValue) => {
        updateOptions(newValue);
        props.onChange(newValue);
      }}
            /* eslint-disable react/jsx-props-no-spreading */

      renderInput={(params) => <TextField
        {...params}
        label={label}
        variant="outlined"
      />}
    />;
  }

  if (label && helpText[label]) {
    return helpText[label];
  }
  /* eslint-disable react/jsx-props-no-spreading */
  return <Widgets.TextWidget {...props} />;
  /* eslint-enable react/jsx-props-no-spreading */
}

function ImageWidget(props) {
  const [changed, setChanged] = React.useState(false);

  const { value, label, id } = props;

  return (
    <>
      {changed && <Alert severity="info">Submit the form to upload the image</Alert>}
      {value && changed && (
        <div style={{ display: 'flex', flexDirection: 'row' }}>
          <img
            src={value}
            alt="profile pic"
            style={{ maxWidth: 300, maxHeight: 300, margin: '8px' }}
          />
        </div>
      )}
      {label} <input
        type="file"
        name={id}
        onChange={(e) => {
          setChanged(true);
          urlToDataURL(URL.createObjectURL(e.target.files[0]), e.target.files[0].name)
            .then((url) => props.onChange(url));
        }}
      />
    </>
  );
}

const formUISchema = {
  bio: {
    'ui:widget': 'textarea',
  },
  avatar: {
    'ui:widget': ImageWidget,
  },
};

export default () => {
  const classes = useStyles();

  const [formData, setFormData] = useState(null);
  const [success, setSuccess] = useState(null);
  const [error, setError] = useState(null);
  const [jsonError, setJsonError] = useState(null);
  const [JSONSchema, setJSONSchema] = useState(null);
  const [requested, setRequested] = useState(false);

  // verify all unverified e-mails
  const verifyEmails = () => {
    const api = new TournesolAPI.UserInformationApi();
    api.userInformationVerifyAllEmailsPartialUpdate(window.user_information_id, null, null);
  };

  const loadFormData = () => {
    const api = new TournesolAPI.UserInformationApi();
    api.userInformationRetrieve(window.user_information_id,
      (_err, data) => {
        if (data) {
          // process raw input data.
          const processData = (dataToProcess) => {
            setFormData(dataToProcess);
            return null;
          };

          urlToDataURL(data.avatar)
            .then((dataURL) => {
              data.avatar = dataURL; // eslint-disable-line no-param-reassign
            })
            .catch(() => {
              delete data.avatar; // eslint-disable-line no-param-reassign
            }).finally(() => {
              processData(data);
            });
        }
      });
  };

  const saveFormData = (e) => {
    const api = new TournesolAPI.UserInformationApi();
    const data = e.formData;

    undefinedToNullValue(data);

    api.userInformationPartialUpdate(window.user_information_id,
      { patchedUserInformationPublicSerializerV2: data },
      (err, _data) => {
        setError(err ? formatError(err) : false);
        setSuccess(!err);
        setFormData(data);

        // reload page on success
        if (!err) {
          setFormData(null);
          setRequested(false);
          setJsonError(null);

          // sending a call to verify all e-mails
          verifyEmails();
        } else {
          setJsonError(errorToJsonError(err));
        }
      });
  };

  // load schema
  if (!formData && !requested) {
    setRequested(true);
    getSchema().then((apiSchema) => {
      const apiSchemaTransformed = {
        ...apiSchema, // eslint-disable-line no-param-reassign
        ...apiSchema.components.schemas.PatchedUserInformationPublicSerializerV2,
      };

      deleteFrom(apiSchemaTransformed.properties, ignoreFields);
      const formJSON = fromOpenAPIToJsonSchema(apiSchemaTransformed);
      formJSON.title = undefined;

      recursiveIterDict(formJSON, (o, k) => {
        if (blacklistTitles.includes(o[k])) {
          o[k] = null; // eslint-disable-line no-param-reassign
        }
      });
      setJSONSchema(formJSON);
      loadFormData();
    });

    return <div className={classes.root}>Loading...</div>;
  }

  return (
    <div className={classes.root}>
      {JSONSchema && (
        <Form
          id="id_userinformation_form"
          schema={JSONSchema}
          uiSchema={formUISchema}
          formData={formData}
          onSubmit={saveFormData}
          widgets={{ TextWidget: HelpOrTextWidget, TextareaWidget: CustomTextAreaWidget }}
          extraErrors={{ form: { __errors: error ? [error] : [] }, ...jsonError }}
          noValidate
        >
          {success && (
          <>
            <Alert
              severity="success"
              className="class_success_data_save class_data_save"
            >
              Data saved
              <Button onClick={() => window.location.reload()}>
                Refresh
              </Button>
            </Alert>
          </>
          )}
          {error && !success && (
          <Alert
            severity="error"
            className="class_error_data_save class_data_save"
          >
            Error saving data: {error}
          </Alert>)}

          <Button
            color="primary"
            variant="contained"
            type="submit"
            id="id_userinfo_submit"
          >Save
          </Button>
        </Form>
      )}

    </div>
  );
};
