import React from 'react';

import Typography from '@material-ui/core/Typography';
import Select from '@material-ui/core/Select';
import MenuItem from '@material-ui/core/MenuItem';

import { TournesolAPI } from '../api';

export default () => {
  const [page, setPage] = React.useState(0);
  const [totalPages, setTotalPages] = React.useState(0);
  const [requested, setRequested] = React.useState(false);
  const [acceptedDomains, setAcceptedDomains] = React.useState([]);

  if (!requested) {
    setRequested(true);
    const api = new TournesolAPI.EmailDomainApi();
    const limit = 50;
    api.emailDomainList({ limit, status: 'ACK', offset: page * limit }, (err, data) => {
      if (!err) setTotalPages(Math.ceil(data.count / limit));
      if (!err) setAcceptedDomains(data.results);
    });
  }

  const changePage = (e) => {
    setAcceptedDomains([]);
    setPage(e.target.value);
    setRequested(false);
  };

  return (
    <div id="domains">
      <Typography variant="h3">Tournesol domains certification</Typography>
      <Typography paragraph>Accepted domains</Typography>
      <ul className="accepted_domains_class">
        {acceptedDomains && acceptedDomains.map((domain) => (
          <li>
            <Typography paragraph>
              <a className="domain_link_class" href={`http://${domain.domain.substring(1)}`}>
                {domain.domain}
              </a>: {domain.n_verified_emails} contributor{domain.n_verified_emails > 1 ? 's' : ''}
            </Typography>
          </li>))}
      </ul>
      <Select value={page} onChange={changePage}>
        {Array.from({ length: totalPages }, (_, i) => (
          <MenuItem key={i} value={i}>Page {i + 1}/{totalPages}</MenuItem>
        ))}
      </Select>
    </div>
  );
};
