import React from 'react';

import { useHistory } from 'react-router-dom';
import IconButton from '@material-ui/core/IconButton';
import { TournesolAPI } from '../api';

export default () => {
  const [requested, setRequested] = React.useState(false);
  const [mentions, setMentions] = React.useState([]);

  const history = useHistory();

  if (!requested) {
    setRequested(true);
    const api = new TournesolAPI.VideoCommentsApi();
    api.videoCommentsList({ comment: `@${window.username}`, limit: 50 }, (err, data) => {
      if (!err) {
        setMentions(data.results);
      }
    });
  }

  /* eslint-disable camelcase */
  return mentions.map(({ datetime_add_ago, video, username }) => (
    <li className="class_li_comment_mention">
      {username} mentioned you {datetime_add_ago} ago on video
      <IconButton onClick={() => history.push(`/details/${video}`)}>
        {video}
      </IconButton>
    </li>));
  /* eslint-enable camelcase */
};
