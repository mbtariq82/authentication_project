import { GoogleLogin } from "@react-oauth/google";

type GoogleLoginButtonProps = {
  onCredential: (idToken: string) => Promise<void>;
  onError: (message: string) => void;
};

export function GoogleLoginButton({
  onCredential,
  onError,
}: GoogleLoginButtonProps) {
  return (
    <GoogleLogin
      onSuccess={async (credentialResponse) => {
        const idToken = credentialResponse.credential;

        if (!idToken) {
          onError("Google did not return an ID token.");
          return;
        }

        try {
          await onCredential(idToken);
        } catch {
          onError("Google login failed.");
        }
      }}
      onError={() => {
        onError("Google login failed.");
      }}
    />
  );
}