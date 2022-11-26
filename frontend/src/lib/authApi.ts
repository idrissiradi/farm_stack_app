import axios from 'axios';

import {
	RegisterRequest,
	UserResponse,
	LoginRequest,
	UserProfile,
	ResetPasswordRequest,
} from './types/userTypes';

// const { NEXT_URL } = process.env;
const BASE_URL = 'http://localhost:8000/api';

const authApi = axios.create({
	baseURL: BASE_URL,
	withCredentials: true,
	headers: {
		'Content-Type': 'application/json',
	},
});

authApi.interceptors.request.use((config) => {
	const token = localStorage.getItem('token');

	if (token) {
		config.headers!.Authorization = `Bearer ${token}`;
	}

	return config;
});

authApi.interceptors.response.use(
	(response) => {
		return response;
	},
	async (error) => {
		const originalRequest = error.config;
		const errMessage = error.response.data.message as string;
		if (errMessage.includes('not logged in') && !originalRequest._retry) {
			originalRequest._retry = true;
			await refreshAccessTokenFn();
			return authApi(originalRequest);
		}
		return Promise.reject(error);
	},
);

export const refreshAccessTokenFn = async () => {
	const response = await authApi.post<string>('/auth/refresh');
	localStorage.setItem('token', response.data);
	return response.data;
};

export const registerUserFn = async (user: RegisterRequest) => {
	const userSubmit = {
		user,
	};
	const response = await authApi.post('/auth/register', userSubmit);
	return response.data;
};

export const loginUserFn = async (user: LoginRequest) => {
	const response = await authApi.post<UserResponse>('/auth/login', user);
	localStorage.setItem('token', response.data.token);
	return response.data;
};

export const logoutUserFn = async () => {
	const response = await authApi.post('/auth/logout');
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
