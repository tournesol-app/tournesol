import React from 'react';
import { render, screen } from '@testing-library/react';

import CriteriaIcon from './CriteriaIcon';

const renderCriteriaIcon = (name: string) =>
  render(<CriteriaIcon criteriaName={name} />);

describe('render CriteriaIcon', () => {
  it('criteria "largely_recommended" uses an img as icon', () => {
    const { container } = renderCriteriaIcon('largely_recommended');
    expect(container.querySelector('img')).toBeVisible();
  });

  it('criteria "international" uses an emoji as icon', () => {
    renderCriteriaIcon('international');
    expect(screen.getByText('🌍')).toBeVisible();
  });
});
