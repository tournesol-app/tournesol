import { Language } from '@mui/icons-material';
import { MenuItem, Box } from '@mui/material';
import React from 'react';
import { useTranslation } from 'react-i18next';
import { SUPPORTED_LANGUAGES } from 'src/i18n';
import MenuButton from './MenuButton';

interface LanguageSelectorProps {
  languageName?: boolean;
}

const codeToLanguage = Object.fromEntries(
  SUPPORTED_LANGUAGES.map((l) => [l.code, l])
);

const LanguageSelector = ({ languageName = true }: LanguageSelectorProps) => {
  const { i18n } = useTranslation();
  const currentLanguage = i18n.resolvedLanguage || i18n.language;

  return (
    <Box
      sx={{
        color: 'neutral.main',
      }}
    >
      <MenuButton
        startIcon={<Language />}
        sx={{
          width: '100%',
          px: '20px',
          justifyContent: 'flex-start',
        }}
        menuContent={SUPPORTED_LANGUAGES.map(({ code, name }) => (
          <MenuItem
            key={code}
            sx={{
              minWidth: '200px',
              '&.Mui-selected': {
                bgcolor: 'action.selected',
              },
              '&.Mui-selected:hover': {
                bgcolor: 'action.selected',
              },
            }}
            onClick={() => i18n.changeLanguage(code)}
            selected={code === currentLanguage}
          >
            <Box component="span" sx={{ textTransform: 'capitalize' }}>
              {name}
            </Box>
            &nbsp;({code})
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
        {languageName && (
          <Box
            sx={{
              flexGrow: 1,
              textAlign: 'left',
              fontWeight: 'bold',
              textTransform: 'capitalize',
            }}
          >
            {codeToLanguage[currentLanguage]?.name ?? currentLanguage}
          </Box>
        )}
      </MenuButton>
    </Box>
  );
};

export default LanguageSelector;
