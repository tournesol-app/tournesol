import React from 'react';
import { Trans } from 'react-i18next';

import { ExternalLink } from 'src/components';

const EngagingDesc = () => (
  <Trans i18nKey="criteriaDescriptions.engaging">
    <em>
      Does it catch people&apos;s attention, spark curiosity and invite to
      question previous beliefs?
    </em>
    <p>
      When judging this quality feature, the contributors are typically invited
      to ask themselves if their relatives would be bored by the content, or if
      the content has a chance to start an interesting discussion or to
      encourage further research on the topic.
    </p>
    <p>
      Contents that score high on &quot;engaging and thought-provoking&quot;
      should catch the attention of a larger audience, trigger their curiosity
      and create a desire to find out more, including by questioning their own
      beliefs.
    </p>
    <h3>Engaging</h3>
    <p>
      The dynamism of the video, the use of humour or the audiovisual quality of
      the story-telling are important components to consider.
    </p>
    <p>
      This{' '}
      <ExternalLink href="https://tournesol.app/entities/yt:QLIKgT-OSLQ">
        Veritasium video
      </ExternalLink>{' '}
      presents advice for more engaging science videos.
    </p>
    <h3>Thought-provoking</h3>
    <p>
      A video is thought-provoking if it invites further, perhaps unusual,
      thoughts for viewers. It may typically be more successful at doing so if
      it raises further questions, encourages viewers to reflect further and
      provides pointers to find out more.
    </p>
    <h3>Curiosity</h3>
    <p>
      As opposed to many metrics including &quot;scientific intelligence&quot;
      <sup>
        (
        <ExternalLink href="https://www.cambridge.org/core/journals/behavioural-public-policy/article/abs/motivated-numeracy-and-enlightened-selfgovernment/EC9F2410D5562EF10B7A5E2539063806">
          KahanPCS-17
        </ExternalLink>
        )
      </sup>
      , scientific curiosity has been linked to a convergence of beliefs despite
      diverging political views{' '}
      <sup>
        (
        <ExternalLink href="https://onlinelibrary.wiley.com/doi/full/10.1111/pops.12396">
          KahanLCHH-17
        </ExternalLink>
        )
      </sup>
      .
    </p>
    <p>
      <ExternalLink href="https://www.penguinrandomhouse.com/books/555240/the-scout-mindset-by-julia-galef/">
        Galef-21
      </ExternalLink>{' '}
      argues that the greatest bottleneck to good judgment is usually the will
      to adopt the &quot;scout mindset&quot;, which is defined as accuracy
      motivated reasoning or intellectual honesty. This is as opposed to the
      &quot;soldier mindset&quot;, which corresponds to belief motivated
      reasoning.
    </p>
  </Trans>
);

export default EngagingDesc;
