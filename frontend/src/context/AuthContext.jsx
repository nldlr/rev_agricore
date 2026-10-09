import { createContext, useContext, useMemo, useState } from "react";
import apiClient from "../api/client";

//create a global React context which acts as a central store to hold authentication
//state so any component can access it without passing props down manually
const AuthContext = createContext(null);

//extracts and decodes the user payload from our JWT so that React can read it
//without calling the backend again
function decodeToken(token) {
    const payloadSegment = token.split('.')[1];
    return JSON.parse(atob(payloadSegment));
}

//AuthProvider is a component that wraps the application and manages authentication state
export function AuthProvider({children}) {

    const [token, setToken] = useState(() => localStorage.getItem('agricoreToken'));

    const user = useMemo(() => (token ? decodeToken(token): null), [token]);

    const login = async (username, password) => {
        const formData = new URLSearchParams();
        formData.append('username', username);
        formData.append('password', password);

        const response = await apiClient.post('/auth/token', formData, {
            headers: {'Content-Type': 'application/x-www-form-urlencoded'},
        });
        localStorage.setItem('agricoreToken', response.data.access_token);
        localStorage.setItem('agricoreRefreshToken', response.data.refresh_token);
        setToken(response.data.access_token);
    }

    const logout = () => {
        localStorage.removeItem('agricoreToken');
        localStorage.removeItem('agricoreRefreshToken')
        setToken(null);
    };

    const value = {token, user, isAuthenticated: Boolean(token), login, logout};

    return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;

}

export function useAuth() {
    const context = useContext(AuthContext);
    if (context === null) {
        throw new Error('useAuth must be used within AuthProvider')
    }
    return context;
}