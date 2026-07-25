const ALLOWED_EMAIL_DOMAIN = "@informationtechconsultants.co.uk";

export function isAllowedEmail(email: string): boolean {
  return email.trim().toLowerCase().endsWith(ALLOWED_EMAIL_DOMAIN);
}