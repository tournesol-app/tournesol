import React from 'react';
import { useTranslation, Trans } from 'react-i18next';

import makeStyles from '@mui/styles/makeStyles';
import {
  Grid2,
  Typography,
  Box,
  Card,
  Link,
  Paper,
  Divider,
  CardContent,
} from '@mui/material';

import { ContentHeader, ExternalLink, ContentBox } from 'src/components';
import {
  discordTournesolInviteUrl,
  githubTournesolUrl,
  linkedInTournesolUrl,
  whitePaperUrl,
} from 'src/utils/url';
import PublicDownloadSection from './PublicDownloadSection';
import { useTheme } from '@mui/styles';

const useStyles = makeStyles(() => ({
  root: {
    width: '100%',
    justifyContent: 'center',
  },
  container: {
    maxWidth: '900px',
    margin: '0 auto',
    display: 'flex',
    justifyContent: 'center',
    padding: 8,
  },
  card: {
    border: '1px solid #DCD8CB',
    padding: '24px',
    background: '#FFFFFF',
  },
}));

const CoreTeamCard = ({
  name,
  image,
  institution,
  role,
  title,
  job,
}: {
  name: string;
  image: string;
  institution: string;
  role?: string;
  title?: string;
  job: string;
}) => {
  return (
    <Card sx={{ maxWidth: 320, fontSize: '0.9rem' }}>
      <CardContent>
        <img
          src={image}
          width="100%"
          style={{
            aspectRatio: '1',
            objectFit: 'cover',
            borderRadius: '50%',
            marginBottom: '8px',
          }}
        />
        <Typography variant="h4">{name}</Typography>
        <div>
          <strong>{role}</strong>
        </div>
        <div>{title}</div>
        <div>{job}</div>
        <div>
          <em>{institution}</em>
        </div>
      </CardContent>
    </Card>
  );
};

const ContributorCard = ({
  name,
  image,
  description,
  website,
}: {
  name: string;
  image: string;
  description: string;
  website: string;
}) => {
  const classes = useStyles();

  return (
    <Link
      href={website}
      rel="noopener"
      underline="none"
      color="inherit"
      variant="inherit"
      sx={{
        display: 'flex',
      }}
    >
      <Card className={classes.card}>
        <Grid2 container spacing={2}>
          <Grid2
            container
            sx={{
              alignItems: 'center',
            }}
            size={4}
          >
            <img
              src={image}
              width="100%"
              style={{
                aspectRatio: '1',
                objectFit: 'cover',
                borderRadius: '50%',
              }}
            />
          </Grid2>
          <Grid2 size={8}>
            <Typography variant="h3">{name}</Typography>
            <Typography
              sx={{
                fontSize: '90%',
              }}
            >
              {description}
            </Typography>
          </Grid2>
        </Grid2>
      </Card>
    </Link>
  );
};

const AboutPage = () => {
  const { t } = useTranslation();
  const classes = useStyles();
  const theme = useTheme();

  return (
    <>
      <ContentHeader title={t('menu.about')} />
      <ContentBox
        maxWidth="md"
        sx={{
          '&': {
            strong: {
              textDecorationLine: 'underline',
              textDecorationColor: theme.palette.primary.main,
              textDecorationThickness: '4px',
              textDecorationSkipInk: 'none',
            },
            h3: {
              mb: 1,
            },
          },
        }}
      >
        <Box my={3}>
          <Typography variant="h3">{t('about.whatIsTournesol')}</Typography>
          <p>
            <Trans i18nKey="about.tournesolIsANonProfit" t={t}>
              Tournesol is a non-profit association working to protect
              democracies against the dangers of unregulated recommendation and
              generative AIs. These AIs shape how we understand the world, but
              without proper governance, they pose systemic risks to our
              societies. On{' '}
              <ExternalLink href="https://tournesol.app/">
                tournesol.app
              </ExternalLink>
              , we are leading a participatory research project to study the
              philosophical principles and desirable mathematical properties
              that algorithms must possess to be secure, democratic, and
              robustly beneficial.
            </Trans>
          </p>
          <p>
            <Trans
              i18nKey="about.weBelieveThatTheDefinitionOfPublicUtility"
              t={t}
            >
              We believe that the definition of &quot;public utility&quot;
              belongs to citizens, not private corporations. By aggregating
              contributors&apos; judgments through our platform, we aim to
              produce the open data and scores necessary to audit industrial
              algorithms and steer the future of AI regulation towards a model
              that serves the general interest.
            </Trans>
          </p>
          <p>
            <Trans i18nKey="about.findOutMore" t={t}>
              Find out more with our{' '}
              <ExternalLink href="/manifesto">manifesto</ExternalLink>,
              <ExternalLink href={whitePaperUrl}>white paper</ExternalLink>,{' '}
              <ExternalLink href={githubTournesolUrl}>GitHub</ExternalLink>,{' '}
              <ExternalLink href={discordTournesolInviteUrl}>
                Discord
              </ExternalLink>
              , or{' '}
              <ExternalLink href={linkedInTournesolUrl}>
                LinkedIn page
              </ExternalLink>
              .
            </Trans>
          </p>
        </Box>

        {/* </ContentBox> */}

        <Divider sx={{ maxWidth: '500px', mx: 'auto', my: 3 }} />

        {/* <ContentBox sx={{ p: 4 }}> */}
        <Box my={3}>
          <Grid2 container className={classes.root}>
            {/* <img height="64px" src="/logos/Tournesol_Logo.png" /> */}
            <Box width="100%">
              <Typography variant="h3">
                {/* {t('about.tournesolAssociation')} */}
                {t('about.currentTeam')}
              </Typography>
              <p>{t('about.tournesolAssociationDetail')}</p>
            </Box>
            <Grid2
              container
              spacing={1}
              sx={{
                justifyContent: 'center',
                '& > .MuiGrid2-root': {
                  display: 'flex',
                },
              }}
            >
              <Grid2
                size={{
                  xs: 6,
                  sm: 4,
                }}
              >
                <CoreTeamCard
                  name="Jean-Lou Fourquet"
                  image="/people/JeanLou.jpg"
                  institution="AprèsLaBière"
                  title=""
                  role={t('about.rolePresident')}
                  job="Journalist & Youtuber"
                />
              </Grid2>

              <Grid2
                size={{
                  xs: 6,
                  sm: 4,
                }}
              >
                <CoreTeamCard
                  name="Titouan Lustin"
                  image="/people/Titouan.jpg"
                  institution="UTC"
                  title="Master of Science"
                  role={t('about.roleVicePresident')}
                  job="Engineer"
                />
              </Grid2>

              <Grid2
                size={{
                  xs: 6,
                  sm: 4,
                }}
              >
                <CoreTeamCard
                  name="Louis Faucon"
                  image="/people/Louis.jpeg"
                  institution="Oracle Labs"
                  role={t('about.roleTreasurer')}
                  title="Dr. in Computer Science"
                  job="Machine Learning Engineer"
                />
              </Grid2>

              <Grid2
                size={{
                  xs: 6,
                  sm: 4,
                }}
              >
                <CoreTeamCard
                  name="Adrien Matissart"
                  image="/people/Adrien.jpeg"
                  institution=""
                  role={t('about.roleSecretary')}
                  job="Senior Software Engineer"
                />
              </Grid2>

              <Grid2
                size={{
                  xs: 6,
                  sm: 4,
                }}
              >
                <CoreTeamCard
                  name="Romain"
                  image="/people/Tournecat.jpeg"
                  institution=""
                  role={t('about.roleViceSecretary')}
                  title=""
                  job="Senior Software Engineer"
                />
              </Grid2>

              <Grid2
                size={{
                  xs: 6,
                  sm: 4,
                }}
              >
                <CoreTeamCard
                  name="Lê Nguyên Hoang"
                  image="/people/Le.jpeg"
                  role="Executive Director"
                  institution=""
                  title="Dr. in Mathematics"
                  job="AI Researcher and Communicator"
                />
              </Grid2>

              <Divider flexItem sx={{ width: '100%', my: 2 }} />

              <Grid2
                size={{
                  xs: 6,
                  sm: 4,
                }}
              >
                <CoreTeamCard
                  name="Victor Fersing"
                  image="/people/Victor.jpg"
                  institution="La Fabrique Sociale"
                  title=""
                  role="Communication & Events"
                  job="Youtuber"
                />
              </Grid2>

              <Grid2
                size={{
                  xs: 6,
                  sm: 4,
                }}
              >
                <CoreTeamCard
                  name="Aidan Jungo"
                  image="/people/Aidan.jpg"
                  institution="SBB CFF FFS"
                  job="Project Manager"
                />
              </Grid2>
            </Grid2>
          </Grid2>
        </Box>

        <Divider sx={{ maxWidth: '500px', mx: 'auto', my: 3 }} />

        <Grid2 container className={classes.root}>
          <Grid2 className={classes.container} size={12}>
            <Box width="100%">
              <Typography variant="h3">
                {t('about.significantContributors')}
              </Typography>
              <Typography>{t('about.weThankOurContributors')}</Typography>
            </Box>
          </Grid2>

          <Grid2 container>
            <Grid2
              className={classes.container}
              size={{
                xs: 12,
                sm: 6,
              }}
            >
              <ContributorCard
                name="Sergei"
                image="/people/Sergei.jpg"
                description={t('about.sergeiDescription')}
                website="https://linkedin.com/in/sergeivolodin"
              />
            </Grid2>
            <Grid2
              className={classes.container}
              size={{
                xs: 12,
                sm: 6,
              }}
            >
              <ContributorCard
                name="Michael Witrant"
                image="/people/sigmike.png"
                description={t('about.sigmikeDescription')}
                website="https://github.com/sigmike"
              />
            </Grid2>
          </Grid2>
        </Grid2>

        <Divider sx={{ maxWidth: '500px', mx: 'auto', my: 3 }} />

        <Grid2 container className={classes.root}>
          <Grid2 className={classes.container} size={12}>
            <Box width="100%">
              <Typography variant="h3">
                {t('about.weThankOurPartners')}
              </Typography>
            </Box>
          </Grid2>

          <Grid2 className={classes.container} size={12}>
            <Link
              href="https://www.calicarpa.com/"
              rel="noopener"
              underline="none"
              color="inherit"
              variant="inherit"
              sx={{
                display: 'flex',
              }}
            >
              <Box className={classes.card} maxWidth="100%">
                <img height="84px" src="/logos/Calicarpa_Logo.svg" />
                <Typography variant="h4">
                  {t('about.partnershipWithCalicarpa')}
                </Typography>
                <Typography paragraph>
                  {t('about.partnershipWithCalicarpaDetail')}
                </Typography>
              </Box>
            </Link>
          </Grid2>

          <Grid2 size={12} className={classes.container}>
            <Box className={classes.card} maxWidth="100%">
              <img height="84px" src="/logos/EPFL_Logo.png" />
              <Typography variant="h4">
                {t('about.partnershipWithEpfl')}
              </Typography>
              <Typography
                sx={{
                  marginBottom: 2,
                }}
              >
                {t('about.partenershipWithEpflDetail')}
              </Typography>
            </Box>
          </Grid2>

          <Grid2
            className={classes.container}
            size={{
              xs: 12,
              md: 6,
            }}
          >
            <Link
              href="https://www.polyconseil.fr/"
              rel="noopener"
              underline="none"
              color="inherit"
              variant="inherit"
              sx={{
                display: 'flex',
              }}
            >
              <Box className={classes.card} maxWidth="100%">
                <img
                  height="64px"
                  src="/logos/Polyconseil_Logo.png"
                  style={{ maxWidth: '100%' }}
                />
                <Typography variant="h4">
                  {t('about.partnershipWithPolyconseil')}
                </Typography>
                <Typography
                  sx={{
                    marginBottom: 2,
                  }}
                >
                  {t('about.partnershipWithPolyconseilDetail')}
                </Typography>
              </Box>
            </Link>
          </Grid2>

          <Grid2
            className={classes.container}
            size={{
              xs: 12,
              md: 6,
            }}
          >
            <Link
              href="https://kleis.ch/"
              rel="noopener"
              underline="none"
              color="inherit"
              variant="inherit"
              sx={{
                display: 'flex',
              }}
            >
              <Box className={classes.card} maxWidth="100%">
                <img height="64px" src="/logos/Kleis_Logo.svg" />
                <Typography variant="h4">
                  {t('about.partnershipWithKleis')}
                </Typography>
                <Typography
                  sx={{
                    marginBottom: 2,
                  }}
                >
                  {t('about.partnershipWithKleisDetail')}
                </Typography>
              </Box>
            </Link>
          </Grid2>

          <Grid2 className={classes.container} size={12}>
            <Link
              href="https://www.devoxx.fr/"
              rel="noopener"
              underline="none"
              color="inherit"
              variant="inherit"
            >
              <Box className={classes.card} maxWidth="100%">
                <img height="64px" src="/logos/devoxx_france_logo.png" />
                <Typography
                  sx={{
                    marginBottom: 2,
                  }}
                >
                  {t('about.collaborationWithDevoxx')}
                </Typography>
              </Box>
            </Link>
          </Grid2>
        </Grid2>
        <Grid2 container className={classes.root}>
          <Grid2 className={classes.container}>
            <Box maxWidth="100%" sx={{ p: 2 }}>
              <img height="64px" src="/logos/Foss_Logo.png" />
              <Typography variant="h4">
                {t('about.openSourceContributions')}
              </Typography>
              <Typography>
                <Trans t={t} i18nKey="about.openSourceContributors">
                  As Tournesol is an open source project, we have been lucky to
                  benefit from contributions by multiple volunteers. Find our
                  wonderful contributors on{' '}
                  <ExternalLink
                    href={`${githubTournesolUrl}/graphs/contributors`}
                  >
                    Github Contributors
                  </ExternalLink>
                </Trans>
              </Typography>
            </Box>
          </Grid2>
        </Grid2>
        <Grid2 container className={classes.root}>
          <Grid2 className={classes.container}>
            <Paper
              sx={{
                bgcolor: 'background.emphatic',
                color: 'white',
                p: 2,
                m: 1,
              }}
            >
              <PublicDownloadSection />
            </Paper>
          </Grid2>
        </Grid2>
      </ContentBox>
    </>
  );
};

export default AboutPage;
