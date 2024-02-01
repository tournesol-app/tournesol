import React, { useState } from 'react';
import { useHistory, useLocation } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { extractVideoId } from 'src/utils/video';
import makeStyles from '@mui/styles/makeStyles';

const useStyles = makeStyles(() => ({
  search: {
    display: 'flex',
    flexDirection: 'row',
    alignItems: 'center',
    height: '100%',
  },
  searchTerm: {
    border: '1px solid #F1EFE7',
    borderRight: 'none',
    padding: '5px',
    height: '36px',
    borderRadius: '4px 0px 0px 4px',
    boxSizing: 'border-box',
    outline: 'none',
    color: '#9dbfaf',
    fontFamily: 'Poppins',
    fontStyle: 'normal',
    fontWeight: 400,
    fontSize: '18px',
    lineHeight: '28px',
    width: '100%',
    maxWidth: 'calc(100% - 76px)',
  },
  searchButton: {
    width: '76px',
    height: '36px',
    border: '1px solid #F1EFE7',
    background: '#F1EFE7',
    color: '#fff',
    cursor: 'pointer',
    borderRadius: '0px 4px 4px 0px',
  },
  searchOpen: {
    cursor: 'pointer',
  },
}));

const Search = () => {
  const { t } = useTranslation();
  const classes = useStyles();
  const history = useHistory();
  const paramsString = useLocation().search;
  const searchParams = new URLSearchParams(paramsString);
  const [search, setSearch] = useState(searchParams.get('search') || '');

  /**
   * Redirect to analysis page when `search` is a:
   * - YouTube URL
   * - Tournesol URL (analysis page)
   * - Tournesol UID
   *
   * ...else redirect to the regular search results.
   *
   * It's not easy to distinguish a YT video id from a string of 11
   * characters, so both case are treated in the same way.
   */
  const onSubmit = (event: React.SyntheticEvent<HTMLFormElement>) => {
    event.preventDefault();
    searchParams.delete('search');
    searchParams.append('search', search);
    searchParams.delete('offset');

    const videoId = extractVideoId(search, { ignoreVideoId: true });

    if (videoId) {
      history.push('/entities/yt:' + videoId.toString());
    } else {
      history.push('/recommendations?' + searchParams.toString());
    }
  };

  return (
    <form onSubmit={onSubmit} className={classes.search}>
      <input
        type="text"
        className={classes.searchTerm}
        id="searchInput"
        defaultValue={search}
        onChange={(e) => setSearch(e.target.value)}
      ></input>
      <button type="submit" className={classes.searchButton}>
        <img src="/svg/Search.svg" alt={t('topbar.search')} />
      </button>
    </form>
  );
};

export default Search;
