'use client';

import Link from 'next/link';

interface Props {
	href: string;
	text: string;
}

const LinkNav = ({ href, text }: Props) => {
	return (
		<>
			<Link href={href} className='mr-5 hover:text-gray-900 hover:text'>
				{text}
			</Link>
		</>
	);
};

// 'bg-violet-500 text-white'
// 												: 'text-gray-900'
// 										} group flex w-full items-center rounded-md px-2 py-2 text-sm

export default LinkNav;
