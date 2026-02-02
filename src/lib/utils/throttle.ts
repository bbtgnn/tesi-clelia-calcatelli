/* eslint-disable @typescript-eslint/no-explicit-any */

export function createThrottled<Args extends any[]>(
	fn: (...args: Args) => void,
	delay: number
): (...args: Args) => void {
	let lastCall = 0;

	return function (...args: Args) {
		const now = Date.now();

		if (now - lastCall >= delay) {
			lastCall = now;
			fn(...args);
		}
	};
}
