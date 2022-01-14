import { Language } from '@mui/icons-material';
import { MenuItem, Box } from '@mui/material';
import React from 'react';
import { useTranslation } from 'react-i18next';
import { SUPPORTED_LANGUAGES } from 'src/i18n';
import MenuButton from './MenuButton';

const getLanguageName = (code: string) => {
  if (!Intl.DisplayNames) {
    return code;
  }
  return new Intl.DisplayNames(code, {
    type: 'language',
  }).of(code);
};

const LanguageSelector = () => {
  const { i18n } = useTranslation();
  const currentLanguage = i18n.resolvedLanguage;

  return (
    <Box color="neutral.main">
      <MenuButton
        startIcon={<Language />}
        sx={{ width: '100%', px: 3 }}
        menuContent={SUPPORTED_LANGUAGES.map((lang) => (
          <MenuItem
            key={lang}
            sx={{
              minWidth: '200px',
              '&.Mui-selected': {
                bgcolor: 'action.selected',
              },
              '&.Mui-selected:hover': {
                bgcolor: 'action.selected',
              },
            }}
            onClick={() => i18n.changeLanguage(lang)}
            selected={lang == currentLanguage}
          >
            <Box component="span" sx={{ textTransform: 'capitalize' }}>
              {getLanguageName(lang)}
            </Box>
            &nbsp;({lang})
          </MenuItem>
        ))}
        menuProps={{
          anchorOrigin: {
            vertical: 'top',
            horizontal: 'center',
          },
          transformOrigin: {
            vertical: 'bottom',
            horizontal: 'center',
          },
        }}
      >
        <Box
          flexGrow={1}
          textAlign="left"
          fontWeight="bold"
          sx={{ textTransform: 'capitalize' }}
        >
          {getLanguageName(currentLanguage)}
        </Box>
      </MenuButton>
    </Box>
  );
};

export default LanguageSelector;
