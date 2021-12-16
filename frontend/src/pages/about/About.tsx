import React from 'react';

import { makeStyles } from '@material-ui/core/styles';
import { Grid, Typography, Box, Card } from '@material-ui/core';

import { ContentHeader } from 'src/components';

const useStyles = makeStyles(() => ({
  root: {
    width: '100%',
    padding: '32px 0px 32px 0px',
    justifyContent: 'center',
  },
  container: {
    display: 'flex',
    justifyContent: 'center',
    padding: 8,
  },
  card: {
    border: '1px solid #DCD8CB',
    boxShadow:
      '0px 0px 8px rgba(0, 0, 0, 0.02), 0px 2px 4px rgba(0, 0, 0, 0.05)',
    borderRadius: 4,
    padding: 8,
    width: '100%',
    background: '#FFFFFF',
  },
}));

const PeopleCard = ({
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
  role: string;
  title: string;
  job: string;
}) => {
  const classes = useStyles();

  return (
    <Card className={classes.card} style={{ maxWidth: 320 }}>
      <img
        src={image}
        width="100%"
        style={{ aspectRatio: '1', objectFit: 'cover', borderRadius: '50%' }}
      />
      <Typography variant="h3">{name}</Typography>
      <Typography>{role}</Typography>
      <Typography>{title}</Typography>
      <Typography>{job}</Typography>
      <Typography>{institution}</Typography>
    </Card>
  );
};

const ContentBox = ({
  children,
  className,
}: {
  children?: React.ReactNode;
  className?: string;
}) => {
  return (
    <Box
      className={className}
      display="flex"
      flexDirection="column"
      maxWidth="640px"
      alignItems="flex-start"
    >
      {children}
    </Box>
  );
};

const AboutPage = () => {
  const classes = useStyles();

  return (
    <>
      <ContentHeader title="About" />
      <Grid
        container
        className={classes.root}
        style={{ background: '#1282B2', color: 'white' }}
      >
        <Grid item xs={12} className={classes.container}>
          <ContentBox>
            <Typography variant="h1">What is Tournesol?</Typography>
            <Typography paragraph>
              Tournesol is an open source platform which aims to collaboratively
              identify top videos of public utility by eliciting
              contributors&apos; judgements on content quality. We hope to
              contribute to making today&apos;s and tomorrow&apos;s large-scale
              algorithms robustly beneficial for all of humanity. Find out more
              with our white paper, our wiki, our github, and our Discord.{' '}
              {/* TODO links */}
            </Typography>
          </ContentBox>
        </Grid>
      </Grid>

      <Grid container className={classes.root}>
        <Grid
          item
          xs={12}
          className={classes.container}
          style={{ textAlign: 'center' }}
        >
          <ContentBox>
            <Typography variant="h3">
              We seek to build the foundations of a robustly beneficial
              algorithmic gouvernance of information at scale
            </Typography>
            <Typography paragraph style={{ width: '100%', marginTop: 16 }}>
              Through raising awareness of the global information crisis
            </Typography>
            <Typography paragraph style={{ width: '100%' }}>
              Through the development of a collaborative platform for evaluation
              and recommendation of online content
            </Typography>
            <Typography paragraph style={{ width: '100%' }}>
              Through research on ethics of algorithms relying on a large and
              reliable database of human judgements
            </Typography>
          </ContentBox>
        </Grid>
      </Grid>

      <Grid
        container
        className={classes.root}
        style={{ background: '#1282B2', color: 'white' }}
      >
        <Grid item xs={12} className={classes.container}>
          <ContentBox>
            <Typography variant="h1">Who builds Tournesol?</Typography>
            <Typography paragraph>
              Tournesol seeks to be an extremely transparent project. All
              contributions to the project are openly visible on our github,
              description of important concepts and Tournesol’s vision can be
              found on our wiki, and discussions that guide the development of
              Tournesol happen openly on our Discord.
            </Typography>
          </ContentBox>
        </Grid>
      </Grid>

      <Grid
        container
        className={classes.root}
        style={{ background: '#FAF8F3' }}
      >
        <Grid item xs={12} className={classes.container}>
          <ContentBox>
            <img height="64px" src="/logos/Tournesol_Logo.png" />
            <Typography variant="h4">Tournesol Association</Typography>
            {/* TODO: Association logo */}

            <Typography paragraph>
              Tournesol is supported by the non-profit Tournesol association
              based in Lausanne, Switzerland.
            </Typography>
          </ContentBox>
        </Grid>

        <Grid item xs={12} sm={4} lg={3} className={classes.container}>
          <PeopleCard
            name="Lê Nguyên Hoang"
            image="/people/Le.jpeg"
            institution="IC School, EPFL"
            role="President"
            title="Dr. in Mathematics"
            job="AI Researcher and Communicator"
          />
        </Grid>

        <Grid item xs={12} sm={4} lg={3} className={classes.container}>
          <PeopleCard
            name="Louis Faucon"
            image="/people/Louis.jpeg"
            institution="MSCI, Inc."
            role="Treasurer"
            title="Dr. in Computer Science"
            job="Software engineer"
          />
        </Grid>

        <Grid item xs={12} sm={4} lg={3} className={classes.container}>
          <PeopleCard
            name="Aidan Jungo"
            image="/people/Aidan.jpg"
            institution="CFS Engineering SA"
            role="Secretary"
            title="Master of Science"
            job="Research Scientist"
          />
        </Grid>
      </Grid>

      <Grid container className={classes.root}>
        <Grid item xs={12} className={classes.container}>
          <ContentBox>
            <img height="84px" src="/logos/EPFL_Logo.png" />
            <Typography variant="h4">Partnership with EPFL</Typography>
            {/* TODO: EPFL logo */}
            <Typography paragraph>
              Today, our main contributor is the Swiss Federal Institute of
              Technology of Lausanne, also known as EPFL. In particular, Adrien
              Matissart is a research scientist from the Distributed Computing
              Laboratory of the School of Computer and Communication Sciences
              who is fully dedicated to the development of the Tournesol
              platform, while many researchers from the Laboratory are designing
              and studying the Tournesol algorithms.
            </Typography>
          </ContentBox>
        </Grid>

        <Grid item xs={12} sm={4} className={classes.container}>
          <PeopleCard
            name="Adrien Matissart"
            image="/people/Adrien.jpeg"
            institution="School ID, EPFL"
            title="title??"
            role="Research Engineer"
            job=""
          />
        </Grid>
      </Grid>

      <Grid
        container
        className={classes.root}
        style={{ background: '#FAF8F3' }}
      >
        <Grid item xs={12} md={6} className={classes.container}>
          <ContentBox className={classes.card}>
            <img
              height="64px"
              src="/logos/Polyconseil_Logo.png"
              style={{ maxWidth: '100%' }}
            />
            <Typography variant="h4">Partnership with Polyconseil</Typography>
            <Typography paragraph>
              We are also supported by the software company PolyConseil, in the
              context of their #Tech4Good program. Since August 2021,
              PolyConseil allocated a software engineering intern one day per
              week to the technical development of Tournesol and supported us on
              a monthly basis through organizational support and UX/UI designs.
              We are very grateful for their help.
            </Typography>
          </ContentBox>
        </Grid>

        <Grid item xs={12} md={6} className={classes.container}>
          <ContentBox className={classes.card}>
            {/* TODO: logo */}
            <Typography variant="h4">Partnership with Kleis</Typography>
            <Typography paragraph>
              We received support from the technology and consulting company
              Kleis who helped us shape our organizational processes, develop
              the vision of our product and adopt efficient developments
              practices. Our partnership with Kleis has been extremely
              impactful.
            </Typography>
          </ContentBox>
        </Grid>
      </Grid>

      <Grid container className={classes.root}>
        <Grid item xs={12} md={6} className={classes.container}>
          <ContentBox>
            <img height="64px" src="/logos/Foss_Logo.png" />
            <Typography variant="h4">Open Source Contributions</Typography>
            <Typography paragraph>
              As Tournesol is an open source project, we have been lucky to
              benefit from contributions by multiple volunteers. Find our
              wonderful contributors on{' '}
              <a
                href="https://github.com/tournesol-app/tournesol/graphs/contributors"
                target="_blank"
                rel="noreferrer"
              >
                Github Contributors
              </a>
            </Typography>
          </ContentBox>
        </Grid>
      </Grid>

      <Grid
        container
        className={classes.root}
        style={{ background: '#1282B2', color: 'white' }}
      >
        <Grid item xs={12} className={classes.container}>
          <ContentBox>
            <Typography variant="h1">Public Database</Typography>
            <Typography paragraph>
              Tournesol aims to benefit research ... Our public database can be
              downloaded by clicking here (TODO). It is published under{' '}
              <a
                href="https://opendatacommons.org/licenses/by/1-0/"
                style={{ color: 'white' }}
              >
                Open Data Commons Attribution License (ODC-By)
              </a>
              .
            </Typography>
            <Typography paragraph>
              Possible thanks to our users ... Finally, we would like to thank
              all of the volunteers who compared videos on Tournesol. We count
              so far about 2500 users who compared 9000 times more than 3000
              videos.
            </Typography>
          </ContentBox>
        </Grid>
      </Grid>
      <Grid container className={classes.root}>
        <Grid item xs={12} className={classes.container}>
          <ContentBox>
            <Typography variant="h1">Something else?</Typography>
            <Typography paragraph>...</Typography>
          </ContentBox>
        </Grid>
      </Grid>
    </>
  );
};

export default AboutPage;
