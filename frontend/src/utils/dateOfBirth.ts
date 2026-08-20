export type DateOfBirthResult =
  | { isValid: true; value?: string }
  | { isValid: false };

export function buildDateOfBirth(
  day: string,
  month: string,
  year: string,
  today = new Date(),
): DateOfBirthResult {
  if (!day && !month && !year) {
    return { isValid: true };
  }

  if (!day || !month || !/^\d{4}$/.test(year)) {
    return { isValid: false };
  }

  const dayNumber = Number(day);
  const monthNumber = Number(month);
  const yearNumber = Number(year);
  const date = new Date(Date.UTC(yearNumber, monthNumber - 1, dayNumber));

  if (
    date.getUTCFullYear() !== yearNumber ||
    date.getUTCMonth() !== monthNumber - 1 ||
    date.getUTCDate() !== dayNumber
  ) {
    return { isValid: false };
  }

  const todayUtc = Date.UTC(
    today.getFullYear(),
    today.getMonth(),
    today.getDate(),
  );
  if (date.getTime() > todayUtc) {
    return { isValid: false };
  }

  return {
    isValid: true,
    value: `${year}-${month.padStart(2, "0")}-${day.padStart(2, "0")}`,
  };
}
