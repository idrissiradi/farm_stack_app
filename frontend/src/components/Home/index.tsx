import { useStateContext } from '../../context';

const Home = () => {
	const stateContext = useStateContext();
	const data = stateContext.state.user;
	return <div>{data ? <h1>{data?.user.email}</h1> : <h1>Home</h1>}</div>;
};

export default Home;
