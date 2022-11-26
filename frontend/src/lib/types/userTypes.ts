export enum UserRole {
	role_owner = 'owner',
	role_staff = 'staff',
	role_client = 'client',
}
export interface User {
	first_name: string;
	last_name: string;
	email: string;
	role: UserRole;
	is_verified: boolean;
	is_active: boolean;
	is_superuser: boolean;
}

export interface UserProfile {
	user: User;
}

export interface UserResponse {
	user: User;
	token: string;
}

export interface RegisterRequest {
	first_name: string;
	last_name: string;
	email: string;
	role: string;
	password: string;
	password_confirm: string;
}

export interface LoginRequest {
	email: string;
	password: string;
}

export interface ResetPasswordRequest {
	password: string;
	password_confirm: string;
	token: string;
}
