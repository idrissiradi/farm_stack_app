import axios from 'axios';

import {
	RegisterRequest,
	UserResponse,
	LoginRequest,
	UserProfile,
	ResetPasswordRequest,
} from './types/userTypes';

const BASE_URL = 'http://localhost:8000/api';

const authApi = axios.create({
	baseURL: BASE_URL,
	withCredentials: true,
	headers: {
		'Content-Type': 'application/json',
	},
});

authApi.interceptors.response.use(
	(response) => {
		return response;
	},
	async (error) => {
		if (error.response.status !== 401) {
			const originalRequest = error.config;
			if (error && !originalRequest._retry) {
				originalRequest._retry = true;
				await refreshAccessTokenFn();
				return authApi(originalRequest);
			}
			return Promise.reject(error.message);
		}
		throw new Error(`Error message : ${error.message} - `, error.code);
	},
);

export const refreshAccessTokenFn = async () => {
	const response = await authApi.post<string>('/auth/refresh');
	if (response.status === 200) {
		localStorage.setItem('token', response.data);
		return response.data;
	}
	throw new Error(`HTTP error ${response.status}`);
};

export const registerUserFn = async (user: RegisterRequest) => {
	const response = await authApi.post('/auth/register', { user: user });
	return response.data;
};

export const loginUserFn = async (user: LoginRequest) => {
	const response = await authApi.post<UserResponse>('/auth/login', user);
	localStorage.setItem('token', response.data.token);
	return response.data;
};

export const logoutUserFn = async () => {
	const response = await authApi.post('/auth/logout');
	localStorage.removeItem('token');
	return response.data;
};

export const getUserFn = async () => {
	const response = await authApi.get<UserProfile>('/auth/profile');
	return response.data;
};

export const RecoverPasswordFn = async (email: string) => {
	const response = await authApi.post(
		`/auth/recover_password?email=${email}`,
	);
	return response.data;
};

export const ResetPasswordFn = async (data: ResetPasswordRequest) => {
	const response = await authApi.post('/auth/reset', data);
	return response.data;
};
