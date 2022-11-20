import { createContext, ReactNode, useContext, useReducer } from 'react';

import { Action, State, stateReducer } from './reducer';

type Dispatch = (action: Action) => void;

const initialState: State = {
	user: null,
};

type StateContextProviderProps = { children: ReactNode };

const StateContext = createContext<
	{ state: State; dispatch: Dispatch } | undefined
>({
	state: initialState,
	dispatch: () => {},
});

const StateContextProvider = ({ children }: StateContextProviderProps) => {
	const [state, dispatch] = useReducer(stateReducer, initialState);
	const value = { state, dispatch };
	return (
		<StateContext.Provider value={value}>{children}</StateContext.Provider>
	);
};

const useStateContext = () => {
	const context = useContext(StateContext);

	if (context) {
		return context;
	}

	throw new Error(
		`useStateContext must be used within a StateContextProvider`,
	);
};

export { StateContextProvider, useStateContext };
