import axios from 'axios';

const apiClient = axios.create({
    baseURL: import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000',
});

apiClient.interceptors.request.use((config) => {
    const token = localStorage.getItem('agricoreToken');
    if (token) {
        config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
}) ;

// Refresh token if given 401 error (access token expired).
apiClient.interceptors.response.use(
    (response) => response,
    async (error) => {
        const originalRequest = error.config;

        // 401 and no refresh yet.
        if (error.response?.status === 401 && !originalRequest._retry) {
            originalRequest._retry = true;
            const refreshToken = localStorage.getItem('agricoreRefreshToken')

            if (refreshToken) {
            try {
                // Call to /auth/refresh
                const { data } = await axios.post(`${apiClient.defaults.baseURL}/auth/refresh`, {
                refresh_token: refreshToken,
                });

                localStorage.setItem('agricoreToken', data.access_token);
                localStorage.setItem('agricoreRefreshToken', data.refresh_token);

                // 3. Update original failed request and retry seamlessly
                originalRequest.headers.Authorization = `Bearer ${data.access_token}`;
                return apiClient(originalRequest);
                } catch (refreshErr) {
                // If refresh token itself expired/failed, boot to login
                localStorage.clear();
                window.location.href = '/login';
                return Promise.reject(refreshErr);
            }
        }
    }
    return Promise.reject(error);
}
);

export default apiClient;