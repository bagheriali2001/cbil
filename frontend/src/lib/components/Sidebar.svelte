<script>
	import { selectedFeatures } from '$lib/store/store.js';
	import { createEventDispatcher } from 'svelte';
	const dispatch = createEventDispatcher();

	let items = [
		{ name: 'Color Mean', id: 'mean' },
		{ name: 'Color Histogram', id: 'hist' },
		{ name: 'GLCM', id: 'glcm' },
		{ name: 'HOG', id: 'hog' },
		{ name: 'Simplified GIST', id: 'gist' },
		{ name: 'DCT', id: 'dct' },
		{ name: 'Wavelet', id: 'wavelet' },
		{ name: 'Harris Corners', id: 'corners' }
	];
	export let isOpen = false;

	let pre_selected = [''];

	/**
	 * @param {string} item
	 */
	function toggleSelection(item) {
		selectedFeatures.update((current) => {
			if (current.includes(item)) {
				return current.filter((i) => i !== item);
			} else {
				return [...current, item];
			}
		});
	}

	function closeSidebar() {
		dispatch('toggleSidebar');
	}
</script>

<div class="sidebar {isOpen ? 'open' : ''}">
	<h3>Select Features</h3>

	<div class="item-list">
		{#each items as item}
			<div
				class="item {$selectedFeatures.includes(item.id) ? 'selected' : ''}"
				role="button"
				tabindex="0"
				on:click={() => toggleSelection(item.id)}
				on:keydown={(e) => (e.key === 'Enter' || e.key === ' ') && toggleSelection(item.id)}
			>
				{item.name}
			</div>
		{/each}
	</div>

	<div class="button-group">
		<button class="confirm-btn" on:click={closeSidebar}>Confirm</button>
		<button class="reset-btn" on:click={() => selectedFeatures.set(['mean'])}>Reset</button>
	</div>
</div>

<style>
	.sidebar {
		position: fixed;
		top: 0;
		right: 0;
		width: 320px;
		height: 100%;
		background: var(--dark-2);
		box-shadow: -2px 0 10px var(--select-primary-shadow);
		transform: translateX(100%);
		transition: transform 0.3s ease-in-out;
		padding: 20px;
		display: flex;
		flex-direction: column;
		justify-content: space-between;
		z-index: 900;
	}

	.sidebar.open {
		transform: translateX(0);
	}

	.sidebar h3 {
		color: var(--features-primary);
		font-weight: 600;
		font-size: large;
		text-align: center;
	}

	.item-list {
		flex-grow: 1;
		overflow-y: auto;
		margin-top: 15px;
		padding-right: 5px;
	}

	.item {
		padding: 12px;
		cursor: pointer;
		background-color: var(--dark-0);
		color: var(--light-4);
		transition: background 0.3s ease;
		border-radius: 5px;
		margin: 5px 0;
		text-align: center;
	}

	.item:hover {
		background: var(--features-secondary-hover);
		color: var(--light-1);
	}

	.item.selected {
		background: var(--features-primary);
		color: var(--light-0);
	}

	.item.selected:hover {
		background: var(--features-primary-hover);
	}

	.button-group {
		display: flex;
		gap: 10px;
		justify-content: center;
		padding: 10px 0;
	}

	.confirm-btn,
	.reset-btn {
		padding: 10px 20px;
		font-size: 16px;
		border-radius: 5px;
		cursor: pointer;
		transition: background-color 0.3s ease;
		border: none;
		color: var(--light-0);
	}

	.confirm-btn {
		background-color: var(--features-primary);
	}

	.confirm-btn:hover {
		background-color: var(--features-primary-hover);
	}

	.reset-btn {
		background-color: var(--reset-primary);
	}

	.reset-btn:hover {
		background-color: var(--reset-primary-hover);
	}
</style>
