import { GoogleLogin } from "@react-oauth/google";

interface GoogleLoginButtonProps {
  onCredential: (idToken: string) => Promise<void>;
  onError: () => void;
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
          onError();
          return;
        }

        await onCredential(idToken);
      }}
      onError={onError}
    />
  );
}