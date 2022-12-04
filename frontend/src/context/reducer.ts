import { UserProfile } from '../lib/types/userTypes';

export type State = {
	user: UserProfile | null;
};

export type Action = {
	type: string;
	payload: State;
};

export const stateReducer = (state: State, action: Action) => {
	switch (action.type) {
		case 'LOGIN': {
			return {
				...state,
				user: action.payload.user,
			};
		}
		case 'LOGOUT':
			return {
				...state,
				user: action.payload.user,
			};
		case 'SET_USER':
			return {
				...state,
				user: action.payload.user,
			};
		default: {
			return state;
		}
	}
};
