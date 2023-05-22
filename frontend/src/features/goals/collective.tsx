export const WEEKLY_COMPARISON_GOAL = 2500;

/**
 * Return an emoji to reward the users for their progression in the weekly
 * collective goal.
 */
export const getWeeklyProgressionEmoji = (progression: number) => {
  if (progression > 125) return '❤️‍🔥';
  if (progression > 100) return '🥳 🎉';
  if (progression > 75) return '🌻';
  if (progression > 50) return '🌷';
  if (progression > 25) return '🍀';
  return '🌱';
};
