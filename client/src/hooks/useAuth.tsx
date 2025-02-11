import { createContext, useContext, useState } from "react";
import { useNavigate } from "react-router-dom";
import useLogin from "./useLogin";
import { AxiosError } from "axios";
import {
  AuthContextType,
  AuthProviderProps,
  User,
  LoginData,
} from "../Interfaces";

const AuthContext = createContext<AuthContextType | null>(null);

const AuthProvider = ({ children }: AuthProviderProps) => {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string>(
    localStorage.getItem("site") || ""
  );
  const [error, setError] = useState<Error | AxiosError | null>(null);
  const navigate = useNavigate();
  const { mutate: login } = useLogin();

  const loginAction = async (data: LoginData): Promise<void> => {
    login(data, {
      onSuccess: (response) => {
        setUser({ id: response.user_id });
        setToken(response.access_token);
        localStorage.setItem("site", response.access_token);
        navigate("/selection");
      },
      onError: (error) => {
        console.error("Login failed:", error);
        setError(error);
        throw error;
      },
    });
  };

  const logOut = (): void => {
    setUser(null);
    setToken("");
    setError(null);
    localStorage.removeItem("site");
    navigate("/");
  };

  return (
    <AuthContext.Provider value={{ token, user, loginAction, logOut, error }}>
      {children}
    </AuthContext.Provider>
  );
};

export default AuthProvider;

export const useAuth = (): AuthContextType => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
};
