import React from 'react';
import Typography from '@material-ui/core/Typography';

import { featureList } from '../../constants';

export const featureLinks = {
  reliability: 'https://wiki.tournesol.app/index.php/Reliable_and_not_misleading',
  pedagogy: 'https://wiki.tournesol.app/index.php/Clear_and_pedagogical',
  importance: 'https://wiki.tournesol.app/index.php/Important_and_actionable',
  engaging: 'https://wiki.tournesol.app/index.php/Engaging_and_thought-provoking',
  backfire_risk: 'https://wiki.tournesol.app/index.php/Resilience_to_backfiring_risks',
  layman_friendly: 'https://wiki.tournesol.app/index.php/Layman-friendly',
  diversity_inclusion: 'https://wiki.tournesol.app/index.php/Diversity_and_inclusion',
  better_habits: 'https://wiki.tournesol.app/index.php/Encourages_better_habits',
  entertaining_relaxing: 'https://wiki.tournesol.app/index.php/Entertaining_and_relaxing',
};

export const featureExplanations = {
  reliability: (
    <Typography paragraph key="reliability">
      <b>Reliability</b> measures how much the information presented in the
      content is trustworthy. Information backed by numerous peer-reviewed
      scientific publications and by scientific consensus can be regarded as
      more reliable. To find out more, please watch{' '}
      <a href="https://www.youtube.com/watch?v=DWzKI4WhSPQ">
        this introductory video by the American Chemical Society
      </a>{' '}
      or read{' '}
      <a href="https://www.sciencemag.org/news/2018/09/meta-analyses-were-supposed-end-scientific-debates-often-they-only-cause-more">
        this more nuanced article from Science
      </a>
      .
    </Typography>
  ),
  pedagogy: (
    <Typography paragraph key="pedagogy">
      <b>Pedagogy</b> measures how much the content allows laymen to improve
      their understanding of the information presented in the content. In
      particular, a very pedagogical content should present the key arguments
      that make the information reliable. To find out more, please watch{' '}
      <a href="https://www.youtube.com/watch?v=GEmuEWjHr5c">
        this video by Veritasium
      </a>
      .
    </Typography>
  ),
  importance: (
    <Typography paragraph key="importance">
      <b>Importance</b> measures how critical it is for users to be exposed to
      the content. Contents that present surprising, neglected and actionable
      information with large-scale impacts can be regarded as more important. To
      find out more, please read{' '}
      <a href="https://80000hours.org/2013/12/a-framework-for-strategically-selecting-a-cause/">
        this article by 80,000 Hours
      </a>
      .
    </Typography>
  ),
  engaging: (
    <Typography paragraph key="engagement">
      <b>Engagement</b> measures how likely users are to actively watch and
      listen to the content, and to take further action after the consumption of
      the content. A very engaging content will typically trigger curiosity and
      a desire to find out more. To find out more, please watch{' '}
      <a href="https://www.youtube.com/watch?v=QLIKgT-OSLQ">
        this video by Veritasium
      </a>
      .
    </Typography>
  ),
  backfire_risk: (
    <Typography paragraph key="backfire_risk">
      <b>Resilience to backfire risks</b> measures how likely a user is to
      negatively react to the information presented, and to increase their
      skepticism towards reliable information. This may be particularly likely
      to occur for contents presented with a strong "us versus them" atmosphere
      on controversial topics, though this also occurs for clean presentation of
      a counter-intuitive scientific concept. We strongly recommend to{' '}
      <a href="https://www.youtube.com/watch?v=eVtCO84MDj8">
        watch this content by Veritasium
      </a>{' '}
      or to read{' '}
      <a href="https://www.pnas.org/content/115/37/9216">
        this scientific paper published in PNAS
      </a>{' '}
      to better measure backfire risks.
    </Typography>
  ),
  layman_friendly: (
    <Typography paragraph key="layman_friendly">

      <b>Layman-friendliness</b>. A more layman-friendly video is one that you would feel
      comfortable recommending to your grandparents or to your 5-year-old nephew.
      An example of layman-friendly non-pedagogical video is a video discussing concepts in a
      very superficial way.
      An example of a non-layman-friendly pedagogical video is any of{' '}
      <a href="https://www.youtube.com/channel/UCYO_jab_esuFRV4b17AJtAw">
        3Blue1Brown
      </a>'s{' '}
      video.
    </Typography>
  ),
  diversity_inclusion: (
    <Typography paragraph key="diversity_inclusion">

      <b>Diversity and Inclusion</b>. More diverse and inclusive content should reflect the great
      diversity of humanity's ethnics, beliefs and preferences. Content that also promote
      unusual views in a respectful and thought-provoking manner may also qualify as more
      diverse.
      Typically,{' '}
      <a href="https://www.youtube.com/watch?v=_JVwyW4zxQ4">
        this video
      </a>{' '}
      may be referred to as high diversity and inclusion.
    </Typography>
  ),
  better_habits: (
    <Typography paragraph key="better_habits">

      <b>Encourages better habits</b>. It aims to highlight content that nudges viewers towards
      better habits, for themselves or for society. These habits may include healthier habits,
      in terms of food, sport activities or mental health. They may also include more
      altruistic habits, such as being kinder to others (including on the Internet), reducing
      our carbon footprint and being wary of our overconfidence. Evidently, contents that do
      not promote better habits should be given lower ratings, while contents that promote
      poor habits, purposely or not, should be given very low ratings.

      Contents that score high on "encourages better habits" should be successful
      at motivating viewers to become better persons.

    </Typography>
  ),
  entertaining_relaxing: (
    <Typography paragraph key="entertaining_relaxing">

      <b>Entertaining and relaxing</b>. Contents that score high on "entertaining and relaxing"
      should entertain and relax viewers

    </Typography>
  ),
};

export default () => (
  <>
    <Typography paragraph>
      On Tournesol you will be asked to compare the contents. You can import the
      content of your choice by copy-pasting its URL, or let Tournesol choose a
      video from our database automatically. The comparisons are done by using
      sliders to say which of the contents is more reliable, pedagogical,
      important, engaging and resilient to backfire risks. Please read the
      explanations below before starting to submit contents comparisons
    </Typography>
    <Typography paragraph>
      <b>Rating privacy.</b>{' '}
      If a video is rated publicly, then the score you assign to this video will be publicly
      accessible. When other users search with your preferences, then a publicly rated video may
      be recommended.

      If a video is rated privately, then the score you assign to this video will not be made
      public. However, your ratings will still affect the Tournesol aggregated scores.
    </Typography>
    {featureList.map((f) => featureExplanations[f])}
    <Typography paragraph>
      Finally, if you have better recommendations of contents about the
      different points discussed here, please{' '}
      <a href="mailto:le-nguyen.hoang@science4all.org">contact us</a>.
    </Typography>
  </>
);
